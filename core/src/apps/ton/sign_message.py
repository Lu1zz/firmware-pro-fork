from typing import TYPE_CHECKING

from trezor import wire
from trezor.crypto.curve import ed25519
from trezor.crypto.hashlib import sha256
from trezor.enums import TonWalletVersion, TonWorkChain
from trezor.lvglui.scrs import lv
from trezor.messages import TonSignedMessage, TonSignMessage, TonTxAck

from apps.common import paths, seed
from apps.common.keychain import Keychain, auto_keychain

from . import ICON, PRIMARY_COLOR, tokens
from .layout import require_confirm_fee, require_show_overview
from .tonsdk.boc._cell import validate_cell_repr
from .tonsdk.contract.token.ft import JettonWallet
from .tonsdk.contract.wallet import Wallets, WalletVersionEnum
from .tonsdk.utils._address import Address

if TYPE_CHECKING:
    from trezor.wire import Context


@auto_keychain(__name__)
async def sign_message(
    ctx: Context, msg: TonSignMessage, keychain: Keychain
) -> TonSignedMessage:
    await paths.validate_path(ctx, keychain, msg.address_n)

    node = keychain.derive(msg.address_n)
    public_key = seed.remove_ed25519_prefix(node.public_key())
    workchain = (
        -1 if msg.workchain == TonWorkChain.MASTERCHAIN else TonWorkChain.BASECHAIN
    )

    if msg.wallet_version == TonWalletVersion.V4R2:
        wallet_version = WalletVersionEnum.v4r2
    else:
        raise wire.DataError("Invalid wallet version.")

    init_data = bytes()

    if msg.init_data_initial_chunk is not None:
        init_data += msg.init_data_initial_chunk

    data_total = msg.init_data_length if msg.init_data_length is not None else 0
    data_left = max(0, data_total - len(init_data))

    while data_left > 0:
        resp = await send_request_chunk(ctx, data_left)
        init_data_chunk = resp.init_data_chunk
        data_left -= len(init_data_chunk)
        init_data += init_data_chunk

    jetton_amount = check_jetton_transfer(msg)

    wallet = Wallets.ALL[wallet_version](
        public_key=public_key, wallet_id=msg.wallet_id, wc=workchain
    )
    address = wallet.address.to_string(
        is_user_friendly=True,
        is_url_safe=True,
        is_bounceable=msg.is_bounceable,
        is_test_only=msg.is_testnet_only,
    )

    # display
    ctx.primary_color, ctx.icon_path = lv.color_hex(PRIMARY_COLOR), ICON
    from trezor.ui.layouts import confirm_final, confirm_unknown_token_transfer

    token = None
    recipient = Address(msg.destination).to_string(True, True)

    if jetton_amount:
        token = tokens.token_by_address("TON_TOKEN", msg.jetton_master_address)

        if token is tokens.UNKNOWN_TOKEN:
            # unknown token, confirm contract address
            if msg.jetton_master_address is None:
                raise ValueError("Address cannot be None")
            await confirm_unknown_token_transfer(ctx, msg.jetton_master_address)

    amount = jetton_amount if jetton_amount else msg.ton_amount
    if amount is None:
        raise ValueError("Amount cannot be None")

    if jetton_amount:
        body = JettonWallet().create_transfer_body(
            Address(msg.destination),
            jetton_amount,
            msg.fwd_fee,
            msg.comment,
            wallet.address,
        )
        payload = body
    else:
        payload = msg.comment

    try:
        digest, boc = wallet.create_transaction_digest(
            to_addr=msg.jetton_wallet_address if jetton_amount else msg.destination,
            amount=msg.ton_amount,
            seqno=msg.seqno,
            expire_at=msg.expire_at,
            payload=payload,
            is_raw_data=msg.is_raw_data,
            send_mode=msg.mode,
            state_init=init_data,
            ext_to=None if jetton_amount else msg.ext_destination,
            ext_amount=None if jetton_amount else msg.ext_ton_amount,
            ext_payload=None if jetton_amount else msg.ext_payload,
        )
    except Exception as e:
        print(e)
        if msg.signing_message_repr is not None:
            validate_cell_repr(msg.signing_message_repr)
            boc = msg.signing_message_repr
            from trezor.ui.layouts import confirm_blind_sign_common

            await confirm_blind_sign_common(ctx, address, msg.signing_message_repr)
            await confirm_final(ctx, "TON")
            digest = sha256(msg.signing_message_repr).digest()
            signature = ed25519.sign(node.private_key(), digest)
            return TonSignedMessage(signature=signature, signning_message=None)
        else:
            raise wire.DataError("Parse boc failed.")

    show_details = await require_show_overview(
        ctx,
        recipient,
        amount,
        token,
    )

    if show_details:
        comment = msg.comment.encode("utf-8") if msg.comment else None
        await require_confirm_fee(
            ctx,
            from_address=address,
            to_address=recipient,
            value=amount,
            token=token,
            raw_data=comment if comment else None,
            is_raw_data=msg.is_raw_data,
        )

    if msg.ext_destination:
        for ext_addr, ext_payload, ext_amount in zip(
            msg.ext_destination, msg.ext_payload, msg.ext_ton_amount
        ):
            show_details = False
            show_details = await require_show_overview(
                ctx,
                ext_addr,
                ext_amount,
                None,
            )
            if show_details:
                ext_comment = ext_payload.encode("utf-8") if ext_payload else None
                await require_confirm_fee(
                    ctx,
                    from_address=address,
                    to_address=ext_addr,
                    value=ext_amount,
                    token=None,
                    raw_data=ext_comment if ext_comment else None,
                    is_raw_data=msg.is_raw_data,
                )
    await confirm_final(ctx, "TON")
    signature = ed25519.sign(node.private_key(), digest)

    return TonSignedMessage(signature=signature, signning_message=boc)


def check_jetton_transfer(msg: TonSignMessage) -> int:
    if msg.jetton_amount is None and msg.jetton_amount_bytes is None:
        return 0
    # fmt: off
    elif msg.jetton_amount_bytes is not None and msg.jetton_master_address is not None:
        return int.from_bytes(msg.jetton_amount_bytes, "big")
    # fmt: on
    elif msg.jetton_amount is not None and msg.jetton_master_address is not None:
        return msg.jetton_amount
    else:
        raise wire.DataError("Invalid jetton transfer message.")


async def send_request_chunk(ctx: wire.Context, data_left: int) -> TonTxAck:
    req = TonSignedMessage()
    if data_left <= 1024:
        req.init_data_length = data_left
    else:
        req.init_data_length = 1024

    return await ctx.call(req, TonTxAck)
