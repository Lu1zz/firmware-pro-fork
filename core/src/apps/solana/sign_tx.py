from typing import TYPE_CHECKING

from storage import device
from trezor import wire
from trezor.crypto.curve import ed25519
from trezor.crypto.hashlib import sha256
from trezor.lvglui.scrs import lv
from trezor.messages import SolanaSignedTx

from apps.common import paths, seed
from apps.common.keychain import auto_keychain

from . import ICON, PRIMARY_COLOR
from .message import Message
from .publickey import PublicKey

from .constents import (  # STAKE_PROGRAM_ID,; VOTE_PROGRAM_ID,
    VERSIONED_HEADER_LEN,
    MAX_DATA_SIZE,
    SPL_ASSOCIATED_TOKEN_ACCOUNT_PROGRAM_ID,
    SPL_MEMO_PROGRAM_ID,
    SPL_TOKEN_PROGRAM_ID,
    SYS_PROGRAM_ID,
    COMPUTE_BUDGET_PROGRAM_ID,
)

if TYPE_CHECKING:
    from trezor.messages import SolanaSignTx
    from apps.common.keychain import Keychain

CURRENT_ALLOWED_PROGRAM_IDS = [
    SYS_PROGRAM_ID,
    SPL_TOKEN_PROGRAM_ID,
    SPL_ASSOCIATED_TOKEN_ACCOUNT_PROGRAM_ID,
    SPL_MEMO_PROGRAM_ID,
    COMPUTE_BUDGET_PROGRAM_ID,
]


@auto_keychain(__name__)
async def sign_tx(
    ctx: wire.Context, msg: SolanaSignTx, keychain: Keychain
) -> SolanaSignedTx:
    # verify msg in length
    check(msg)

    # path
    await paths.validate_path(ctx, keychain, msg.address_n)

    node = keychain.derive(msg.address_n)
    signer_pub_key_bytes = seed.remove_ed25519_prefix(node.public_key())

    is_versioned_message = False
    # parse message
    try:
        message, is_versioned_message = Message.deserialize(msg.raw_tx)
    except BaseException as e:
        raise wire.DataError(f"Invalid message {e}")
    sigs_count = message.header.num_required_signatures
    multiple_signers = sigs_count > 1  # noqa: F841
    accounts_keys = message.account_keys
    fee_payer = accounts_keys[0]
    # verify fee payer
    if not multiple_signers:
        if fee_payer.get() != signer_pub_key_bytes:
            if __debug__:
                print(
                    f"Invalid signer used: {PublicKey(fee_payer.get())} != {PublicKey(signer_pub_key_bytes)}"
                )
            raise wire.DataError("Invalid signer used")
    else:
        if PublicKey(signer_pub_key_bytes) not in accounts_keys[:sigs_count]:
            raise wire.DataError("Invalid transaction params")

    # recent_blockhash is something like nonce in ethereum
    _recent_blockhash = message.recent_blockhash  # noqa: F841
    should_blind_sign = is_versioned_message or any(
        accounts_keys[i.program_id_index] not in CURRENT_ALLOWED_PROGRAM_IDS
        for i in message.instructions
    )
    ctx.primary_color, ctx.icon_path = lv.color_hex(PRIMARY_COLOR), ICON

    if device.is_turbomode_enabled() and not isinstance(ctx, wire.QRContext):
        from trezor.lvglui.i18n import gettext as _, keys as i18n_keys
        from trezor.ui.layouts.lvgl import confirm_turbo

        await confirm_turbo(ctx, _(i18n_keys.MSG__SIGN_TRANSACTION), "Solana")
    else:

        if should_blind_sign:
            from trezor.ui.layouts.lvgl import confirm_sol_blinding_sign
            from apps.common.signverify import decode_message

            message_hex = decode_message(sha256(msg.raw_tx).digest())
            await confirm_sol_blinding_sign(ctx, str(fee_payer), message_hex)
        else:
            # enumerate instructions in message
            for i in message.instructions:
                program_id = accounts_keys[i.program_id_index]
                accounts = [accounts_keys[ix] for ix in i.accounts]
                if program_id == SYS_PROGRAM_ID:
                    from .system.program import parse

                    await parse(ctx, accounts, i.data)
                elif program_id == SPL_TOKEN_PROGRAM_ID:
                    from .spl.spl_token_program import parse

                    await parse(ctx, accounts, i.data)
                elif program_id == SPL_ASSOCIATED_TOKEN_ACCOUNT_PROGRAM_ID:
                    from .spl.ata_program import parse

                    await parse(ctx, accounts, i.data)
                elif program_id == SPL_MEMO_PROGRAM_ID:
                    from .spl.memo.memo_program import parse

                    await parse(
                        ctx, accounts if len(accounts) > 0 else [fee_payer], i.data
                    )
            # # elif program_id == STAKE_PROGRAM_ID:
            # #     raise wire.ProcessError("Stake program not support for now")
            # # elif program_id == VOTE_PROGRAM_ID:
            # #     raise wire.ProcessError("Vote program not support for now")
            # else:
            #     print("Unknown instruction detached")
        from trezor.ui.layouts import confirm_final

        await confirm_final(ctx, "SOL")
    signature = ed25519.sign(node.private_key(), msg.raw_tx)
    return SolanaSignedTx(signature=signature)


def check(msg: SolanaSignTx):
    raw_message = msg.raw_tx
    raw_message_len = len(raw_message)
    if raw_message_len > MAX_DATA_SIZE:
        raise wire.DataError("Message overflow")
    elif len(raw_message) < VERSIONED_HEADER_LEN:
        raise wire.DataError("Message too short")
