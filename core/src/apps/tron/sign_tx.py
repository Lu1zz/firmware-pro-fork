from trezor import utils, wire
from trezor.crypto.curve import secp256k1
from trezor.crypto.hashlib import sha256
from trezor.lvglui.scrs import lv
from trezor.messages import TronSignedTx, TronSignTx
from trezor.ui.layouts import confirm_final

from apps.common import paths
from apps.common.keychain import Keychain, auto_keychain
from apps.tron.address import address_base58, get_address_from_public_key
from apps.tron.serialize import serialize

from . import ICON, PRIMARY_COLOR, layout, tokens


@auto_keychain(__name__)
async def sign_tx(
    ctx: wire.Context, msg: TronSignTx, keychain: Keychain
) -> TronSignedTx:
    """Parse and sign TRX transaction"""

    validate(msg)
    address_n = msg.address_n
    await paths.validate_path(ctx, keychain, address_n)
    node = keychain.derive(address_n)

    seckey = node.private_key()
    if utils.USE_THD89:
        from trezor.crypto import se_thd89

        public_key = se_thd89.uncompress_pubkey("secp256k1", node.public_key())
    else:
        public_key = secp256k1.publickey(seckey, False)
    address = get_address_from_public_key(public_key[:65])
    ctx.primary_color, ctx.icon_path = lv.color_hex(PRIMARY_COLOR), ICON
    try:
        await _require_confirm_by_type(ctx, msg, address)
    except AttributeError:
        raise wire.DataError("The transaction has invalid asset data field")

    raw_data = serialize(msg, address)
    data_hash = sha256(raw_data).digest()

    signature = secp256k1.sign(seckey, data_hash, False)

    signature = signature[1:65] + bytes([(~signature[0] & 0x01) + 27])
    return TronSignedTx(signature=signature, serialized_tx=raw_data)


async def _require_confirm_by_type(ctx, transaction, owner_address):

    # Confirm transaction
    contract = transaction.contract
    skip_view_data = False
    if contract.transfer_contract:
        if contract.transfer_contract.amount is None:
            raise wire.DataError("Invalid Tron transfer amount")

        await layout.require_confirm_tx(
            ctx,
            owner_address,
            contract.transfer_contract.to_address,
            contract.transfer_contract.amount,
        )
    elif contract.trigger_smart_contract:
        # check if TRC20 transfer/approval
        data = contract.trigger_smart_contract.data
        action = None

        if data is None:
            raise wire.DataError("Invalid Tron contract call data")

        if (
            data[:16]
            == b"\xa9\x05\x9c\xbb\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        ):
            action = "Transfer"
        elif (
            data[:16]
            == b"\x09\x5e\xa7\xb3\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        ):
            action = "Approve"

        if action == "Transfer":
            token = tokens.token_by_address(
                contract.trigger_smart_contract.contract_address
            )
            recipient = address_base58(b"\x41" + data[16:36])
            value = int.from_bytes(data[36:68], "big")

            if token is tokens.UNKNOWN_TOKEN:
                # unknown token, confirm contract address
                await layout.require_confirm_unknown_token(
                    ctx, contract.trigger_smart_contract.contract_address
                )

            await layout.require_confirm_tx(
                ctx,
                owner_address,
                recipient,
                value,
                token,
            )
        else:
            from trezor.ui.layouts.lvgl import confirm_blind_sign_common

            await confirm_blind_sign_common(ctx, owner_address, data)
    elif contract.freeze_balance_contract:
        await layout.require_confirm_freeze(
            ctx,
            owner_address,
            contract.freeze_balance_contract.frozen_balance,
            contract.freeze_balance_contract.frozen_duration,
            contract.freeze_balance_contract.resource,
            contract.freeze_balance_contract.receiver_address,
        )
    elif contract.unfreeze_balance_contract:
        await layout.require_confirm_unfreeze(
            ctx,
            owner_address,
            contract.unfreeze_balance_contract.resource,
            contract.unfreeze_balance_contract.receiver_address,
            None,
        )
    elif contract.withdraw_balance_contract:
        from trezor.ui.layouts.lvgl import confirm_tron_common

        await confirm_tron_common(ctx, "Withdraw Balance Contract")
    elif contract.freeze_balance_v2_contract:
        await layout.require_confirm_freeze(
            ctx,
            owner_address,
            contract.freeze_balance_v2_contract.frozen_balance,
            None,
            contract.freeze_balance_v2_contract.resource,
            None,
        )
    elif contract.unfreeze_balance_v2_contract:
        await layout.require_confirm_unfreeze_v2(
            ctx,
            owner_address,
            contract.unfreeze_balance_v2_contract.resource,
            contract.unfreeze_balance_v2_contract.unfreeze_balance,
        )
    elif contract.withdraw_expire_unfreeze_contract:
        from trezor.ui.layouts.lvgl import confirm_tron_common

        await confirm_tron_common(ctx, "Withdraw Expire Unfreeze Contract")
    elif contract.delegate_resource_contract:
        await layout.require_confirm_delegate(
            ctx,
            owner_address,
            contract.delegate_resource_contract.resource,
            contract.delegate_resource_contract.balance,
            contract.delegate_resource_contract.receiver_address,
            contract.delegate_resource_contract.lock,
        )
    elif contract.undelegate_resource_contract:
        await layout.require_confirm_undelegate(
            ctx,
            owner_address,
            contract.undelegate_resource_contract.resource,
            contract.undelegate_resource_contract.balance,
            contract.undelegate_resource_contract.receiver_address,
            None,
        )
    elif contract.cancel_all_unfreeze_v2_contract:
        await layout.require_confirm_cancel_all_unfreeze_v2(
            ctx,
            owner_address,
        )
    elif contract.vote_witness_contract:
        vote_contract = contract.vote_witness_contract
        await layout.require_confirm_vote_witness(
            ctx,
            owner_address,
            [(vote.vote_address, vote.vote_count) for vote in vote_contract.votes],
            vote_contract.support,
        )
    else:
        raise wire.DataError("Invalid transaction type")

    # Confirm extra data if exist
    if transaction.data and not skip_view_data:
        await layout.require_confirm_data(ctx, transaction.data, len(transaction.data))

    await confirm_final(ctx, "TRON")


def validate(msg: TronSignTx):
    if None in (msg.contract,):
        raise wire.ProcessError("Some of the required fields are missing (contract)")
