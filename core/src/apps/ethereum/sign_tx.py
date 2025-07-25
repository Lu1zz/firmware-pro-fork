from typing import TYPE_CHECKING

from trezor import wire
from trezor.crypto import rlp
from trezor.crypto.curve import secp256k1
from trezor.crypto.hashlib import sha3_256
from trezor.messages import EthereumSignTx, EthereumTxAck, EthereumTxRequest
from trezor.ui.layouts import confirm_final
from trezor.utils import HashWriter

from apps.common import paths

from . import networks, tokens
from .helpers import (
    address_from_bytes,
    bytes_from_address,
    get_color_and_icon,
    get_display_network_name,
)
from .keychain import with_keychain_from_chain_id
from .layout import (
    require_confirm_data,
    require_confirm_fee,
    require_confirm_unknown_token,
    require_show_overview,
)

if TYPE_CHECKING:
    from apps.common.keychain import Keychain

    from .definitions import Definitions
    from .keychain import EthereumSignTxAny


# Maximum chain_id which returns the full signature_v (which must fit into an uint32).
# chain_ids larger than this will only return one bit and the caller must recalculate
# the full value: v = 2 * chain_id + 35 + v_bit
MAX_CHAIN_ID = (0xFFFF_FFFF - 36) // 2


@with_keychain_from_chain_id
async def sign_tx(
    ctx: wire.Context, msg: EthereumSignTx, keychain: Keychain, defs: Definitions
) -> EthereumTxRequest:
    check(msg)
    await paths.validate_path(ctx, keychain, msg.address_n, force_strict=False)

    # Handle ERC20s
    token, address_bytes, recipient, value = await handle_erc20(ctx, msg)

    data_total = msg.data_length
    network = defs.network
    ctx.primary_color, ctx.icon_path = get_color_and_icon(
        network.chain_id if network else None
    )
    is_nft_transfer = False
    token_id = None
    from_addr = None
    if token is None:
        res = await handle_erc_721_or_1155(ctx, msg)
        if res is not None:
            is_nft_transfer = True
            from_addr, recipient, token_id, value = res
    has_raw_data = token is None and token_id is None and msg.data_length > 0
    show_details = await require_show_overview(
        ctx,
        recipient,
        value,
        int.from_bytes(msg.gas_price, "big"),
        int.from_bytes(msg.gas_limit, "big"),
        msg.chain_id,
        token,
        address_from_bytes(address_bytes, network) if token else None,
        is_nft_transfer,
        has_raw_data,
    )

    if show_details:
        node = keychain.derive(msg.address_n, force_strict=False)
        recipient_str = address_from_bytes(recipient, network)
        from_str = address_from_bytes(from_addr or node.ethereum_pubkeyhash(), network)
        await require_confirm_fee(
            ctx,
            value,
            int.from_bytes(msg.gas_price, "big"),
            int.from_bytes(msg.gas_limit, "big"),
            msg.chain_id,
            token,
            from_address=from_str,
            to_address=recipient_str,
            contract_addr=address_from_bytes(address_bytes, network)
            if token_id is not None
            else None,
            token_id=token_id,
            evm_chain_id=None
            if network is not networks.UNKNOWN_NETWORK
            else msg.chain_id,
            raw_data=msg.data_initial_chunk if has_raw_data else None,
        )

    data = bytearray()
    data += msg.data_initial_chunk
    data_left = data_total - len(msg.data_initial_chunk)

    total_length = get_total_length(msg, data_total)

    sha = HashWriter(sha3_256(keccak=True))
    rlp.write_header(sha, total_length, rlp.LIST_HEADER_BYTE)

    if msg.tx_type is not None:
        rlp.write(sha, msg.tx_type)

    for field in (msg.nonce, msg.gas_price, msg.gas_limit, address_bytes, msg.value):
        rlp.write(sha, field)

    if data_left == 0:
        rlp.write(sha, data)
    else:
        rlp.write_header(sha, data_total, rlp.STRING_HEADER_BYTE, data)
        sha.extend(data)

    while data_left > 0:
        resp = await send_request_chunk(ctx, data_left)
        data_left -= len(resp.data_chunk)
        sha.extend(resp.data_chunk)

    # eip 155 replay protection
    rlp.write(sha, msg.chain_id)
    rlp.write(sha, 0)
    rlp.write(sha, 0)

    digest = sha.get_digest()
    result = sign_digest(msg, keychain, digest)
    await confirm_final(ctx, get_display_network_name(network))
    return result


async def handle_erc20(
    ctx: wire.Context, msg: EthereumSignTxAny
) -> tuple[tokens.EthereumTokenInfo | None, bytes, bytes, int]:
    token = None
    address_bytes = recipient = bytes_from_address(msg.to)
    value = int.from_bytes(msg.value, "big")
    if (
        len(msg.to) in (40, 42)
        and len(msg.value) == 0
        and msg.data_length == 68
        and len(msg.data_initial_chunk) == 68
        and msg.data_initial_chunk[:16]
        == b"\xa9\x05\x9c\xbb\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    ):
        token = tokens.token_by_chain_address(msg.chain_id, address_bytes)
        recipient = msg.data_initial_chunk[16:36]
        value = int.from_bytes(msg.data_initial_chunk[36:68], "big")

        if token is tokens.UNKNOWN_TOKEN:
            await require_confirm_unknown_token(ctx, address_bytes)

    return token, address_bytes, recipient, value


async def handle_erc_721_or_1155(
    ctx: wire.Context, msg: EthereumSignTxAny
) -> None | tuple[bytes, bytes, int, int]:

    from_addr = recipient = None
    token_id = 0
    value = 0
    if (
        len(msg.to) in (40, 42)
        and len(msg.value) == 0
        and msg.data_length
        == 228  # assume data is 00 aka the recipient is not a contract
        and len(msg.data_initial_chunk) == 228
        and msg.data_initial_chunk[:16]
        == b"\xf2\x42\x43\x2a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"  # erc1155 f242432a == keccak("safeTransferFrom(address,address,uint256,uint256,bytes)")[:4].hex()
    ):
        from_addr = msg.data_initial_chunk[16:36]
        recipient = msg.data_initial_chunk[48:68]
        token_id = int.from_bytes(msg.data_initial_chunk[68:100], "big")

        value = int.from_bytes(msg.data_initial_chunk[100:132], "big")
        assert (
            int.from_bytes(msg.data_initial_chunk[132:164], "big") == 0xA0
        )  # dyn data position
        data_len = int.from_bytes(msg.data_initial_chunk[164:196], "big")
        data = msg.data_initial_chunk[-data_len:]
        if not (data_len == 1 and data == b"\x00"):
            await require_confirm_data(ctx, data, data_len)
    elif (
        len(msg.to) in (40, 42)
        and len(msg.value) == 0
        and msg.data_length == 100
        and len(msg.data_initial_chunk) == 100
        and msg.data_initial_chunk[:16]
        == b"\x42\x84\x2e\x0e\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"  # erc721 42842e0e ==  keccak("safeTransferFrom(address,address,uint256)")[:4].hex()
    ):
        from_addr = msg.data_initial_chunk[16:36]
        recipient = msg.data_initial_chunk[48:68]
        token_id = int.from_bytes(msg.data_initial_chunk[68:100], "big")
        value = 1
    if from_addr:
        assert recipient is not None
        return from_addr, recipient, token_id, value
    else:
        return None


def get_total_length(msg: EthereumSignTx, data_total: int) -> int:
    length = 0
    if msg.tx_type is not None:
        length += rlp.length(msg.tx_type)

    fields: tuple[rlp.RLPItem, ...] = (
        msg.nonce,
        msg.gas_price,
        msg.gas_limit,
        bytes_from_address(msg.to),
        msg.value,
        msg.chain_id,
        0,
        0,
    )

    for field in fields:
        length += rlp.length(field)

    length += rlp.header_length(data_total, msg.data_initial_chunk)
    length += data_total

    return length


async def send_request_chunk(ctx: wire.Context, data_left: int) -> EthereumTxAck:
    # TODO: layoutProgress ?
    req = EthereumTxRequest()
    if data_left <= 1024:
        req.data_length = data_left
    else:
        req.data_length = 1024

    return await ctx.call(req, EthereumTxAck)


def sign_digest(
    msg: EthereumSignTx, keychain: Keychain, digest: bytes
) -> EthereumTxRequest:
    node = keychain.derive(msg.address_n, force_strict=False)
    signature = secp256k1.sign(
        node.private_key(), digest, False, secp256k1.CANONICAL_SIG_ETHEREUM
    )

    req = EthereumTxRequest()
    req.signature_v = signature[0]
    if msg.chain_id > MAX_CHAIN_ID:
        req.signature_v -= 27
    else:
        req.signature_v += 2 * msg.chain_id + 8

    req.signature_r = signature[1:33]
    req.signature_s = signature[33:]

    return req


def check(msg: EthereumSignTx) -> None:
    if msg.tx_type not in [1, 6, None]:
        raise wire.DataError("tx_type out of bounds")

    if len(msg.gas_price) + len(msg.gas_limit) > 30:
        raise wire.DataError("Fee overflow")

    check_common_fields(msg)


def check_common_fields(msg: EthereumSignTxAny) -> None:
    if msg.data_length > 0:
        if not msg.data_initial_chunk:
            raise wire.DataError("Data length provided, but no initial chunk")
        # Our encoding only supports transactions up to 2^24 bytes. To
        # prevent exceeding the limit we use a stricter limit on data length.
        if msg.data_length > 16_000_000:
            raise wire.DataError("Data length exceeds limit")
        if len(msg.data_initial_chunk) > msg.data_length:
            raise wire.DataError("Invalid size of initial chunk")

    if len(msg.to) not in (0, 40, 42):
        raise wire.DataError("Invalid recipient address")

    if not msg.to and msg.data_length == 0:
        # sending transaction to address 0 (contract creation) without a data field
        raise wire.DataError("Contract creation without data")

    if msg.chain_id == 0:
        raise wire.DataError("Chain ID out of bounds")
