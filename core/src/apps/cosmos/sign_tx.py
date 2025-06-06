from trezor import wire
from trezor.crypto import bech32
from trezor.crypto.curve import secp256k1
from trezor.crypto.hashlib import sha256
from trezor.crypto.scripts import sha256_ripemd160
from trezor.lvglui.i18n import gettext as _, keys as i18n_keys
from trezor.lvglui.scrs import lv
from trezor.messages import CosmosSignedTx, CosmosSignTx
from trezor.ui.layouts.lvgl import (
    confirm_cosmos_delegate,
    confirm_cosmos_send,
    confirm_cosmos_sign_combined,
    confirm_cosmos_sign_common,
    confirm_final,
    cosmos_require_show_more,
)

import ujson as json
from apps.common import paths
from apps.common.keychain import Keychain, auto_keychain

from .networks import formatAmont, getChainHrp, retrieve_theme_by_hrp
from .transaction import DelegateTxn, SendTxn, Transaction


@auto_keychain(__name__)
async def sign_tx(
    ctx: wire.Context, msg: CosmosSignTx, keychain: Keychain
) -> CosmosSignedTx:

    await paths.validate_path(ctx, keychain, msg.address_n)
    node = keychain.derive(msg.address_n)
    public_key = node.public_key()
    privkey = node.private_key()

    # parse message
    try:
        tx = Transaction.deserialize(msg.raw_tx)
    except BaseException as e:
        raise wire.DataError(f"Invalid message: {e}")

    hrp = getChainHrp(tx.chain_id)
    chain_name = tx.chain_name
    if hrp is None:
        signer = None
    else:
        h = sha256_ripemd160(public_key).digest()
        convertedbits = bech32.convertbits(h, 8, 5)
        assert convertedbits is not None, "Unsuccessful bech32.convertbits call"
        signer = bech32.bech32_encode(hrp, convertedbits, bech32.Encoding.BECH32)
    _chain_name, primary_color, ctx.icon_path = retrieve_theme_by_hrp(hrp)
    ctx.primary_color = lv.color_hex(primary_color)
    if tx.amount is not None and tx.denom is not None:
        fee = formatAmont(tx.chain_id, tx.amount, tx.denom)
    else:
        fee = _(i18n_keys.LIST_VALUE__NONE)
    if len(tx.msgs) == 1:
        tx.display(tx.msgs[0], 0, "msgs")
        tx.tx_display_make_friendly()

        if type(tx.tx) == SendTxn:
            to = tx.tx.to if type(tx.tx) is SendTxn else ""
            from_addr = tx.tx.from_address if type(tx.tx) is SendTxn else ""
            amount = tx.tx.amount if type(tx.tx) is SendTxn else ""
            if await cosmos_require_show_more(
                ctx, None, None, to, amount, chain_name=chain_name
            ):
                await confirm_cosmos_send(
                    ctx,
                    fee,
                    tx.chain_id,
                    amount,
                    chain_name,
                    from_addr,
                    to,
                    tx.memo,
                )
        elif type(tx.tx) == DelegateTxn:
            delegator = tx.tx.delegator if type(tx.tx) is DelegateTxn else ""
            validator = tx.tx.validator if type(tx.tx) is DelegateTxn else ""
            amount = tx.tx.amount if type(tx.tx) is DelegateTxn else ""
            if await cosmos_require_show_more(
                ctx,
                tx.tx.i18n_title,
                tx.tx.i18n_value,
                None,
                None,
                chain_name=chain_name,
            ):
                await confirm_cosmos_delegate(
                    ctx,
                    fee,
                    tx.chain_id,
                    chain_name,
                    delegator,
                    validator,
                    amount,
                    tx.memo,
                )
        else:
            if await cosmos_require_show_more(
                ctx,
                tx.tx.i18n_title,
                tx.tx.i18n_value,
                None,
                None,
                chain_name=chain_name,
            ):
                await confirm_cosmos_sign_common(
                    ctx,
                    tx.chain_id,
                    chain_name,
                    signer,
                    fee,
                    tx.msgs_item,
                    tx.tx.i18n_title,
                    tx.tx.i18n_value,
                    tx.memo,
                )
    else:
        await confirm_cosmos_sign_combined(
            ctx, tx.chain_id, signer, fee, json.dumps(tx.msgs)
        )

    await confirm_final(ctx, chain_name or "Cosmos")

    data_hash = sha256(msg.raw_tx).digest()
    signature = secp256k1.sign(privkey, data_hash, False)[1:]

    return CosmosSignedTx(signature=signature)
