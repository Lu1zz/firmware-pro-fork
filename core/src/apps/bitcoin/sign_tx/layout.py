from micropython import const
from typing import TYPE_CHECKING
from ubinascii import hexlify

from trezor import utils, wire
from trezor.enums import AmountUnit, ButtonRequestType, OutputScriptType
from trezor.lvglui.i18n import gettext as _, keys as i18n_keys
from trezor.strings import format_amount, format_timestamp
from trezor.ui import layouts

from .. import addresses
from ..common import format_fee_rate
from . import omni

if not utils.BITCOIN_ONLY:
    from trezor.ui.layouts.lvgl import altcoin


if TYPE_CHECKING:
    from typing import Any

    from trezor.messages import TxAckPaymentRequest, TxOutput

    from apps.common.coininfo import CoinInfo

_LOCKTIME_TIMESTAMP_MIN_VALUE = const(500_000_000)


def format_coin_amount(amount: int, coin: CoinInfo, amount_unit: AmountUnit) -> str:
    decimals, shortcut = coin.decimals, coin.coin_shortcut
    if amount_unit == AmountUnit.SATOSHI:
        decimals = 0
        shortcut = "sat"
        if coin.coin_shortcut != "BTC":
            shortcut += " " + coin.coin_shortcut
    elif amount_unit == AmountUnit.MICROBITCOIN and decimals >= 6:
        decimals -= 6
        shortcut = "u" + shortcut
    elif amount_unit == AmountUnit.MILLIBITCOIN and decimals >= 3:
        decimals -= 3
        shortcut = "m" + shortcut
    # we don't need to do anything for AmountUnit.BITCOIN
    return f"{format_amount(amount, decimals)} {shortcut}"


async def confirm_output(
    ctx: wire.Context, output: TxOutput, coin: CoinInfo, amount_unit: AmountUnit
) -> None:
    if output.script_type == OutputScriptType.PAYTOOPRETURN:
        data = output.op_return_data
        assert data is not None
        if omni.is_valid(data):
            # OMNI transaction
            layout = layouts.confirm_metadata(
                ctx,
                "omni_transaction",
                "OMNI transaction",
                omni.parse(data),
                br_code=ButtonRequestType.ConfirmOutput,
            )
        else:
            # generic OP_RETURN
            layout = confirm_op_return(ctx, data, output.amount, coin)
    else:
        assert output.address is not None
        address_short = addresses.address_short(coin, output.address)

        layout = layouts.confirm_output(
            ctx,
            address_short,
            format_coin_amount(output.amount, coin, amount_unit),
        )

    await layout


async def confirm_decred_sstx_submission(
    ctx: wire.Context, output: TxOutput, coin: CoinInfo, amount_unit: AmountUnit
) -> None:
    assert output.address is not None
    address_short = addresses.address_short(coin, output.address)

    await altcoin.confirm_decred_sstx_submission(
        ctx, address_short, format_coin_amount(output.amount, coin, amount_unit)
    )


async def confirm_payment_request(
    ctx: wire.Context,
    msg: TxAckPaymentRequest,
    coin: CoinInfo,
    amount_unit: AmountUnit,
) -> Any:
    memo_texts = []
    for m in msg.memos:
        if m.text_memo is not None:
            memo_texts.append(m.text_memo.text + " ")
        elif m.refund_memo is not None:
            pass
        elif m.coin_purchase_memo is not None:
            memo_texts.append(f" Buying {m.coin_purchase_memo.amount}.")
        else:
            raise wire.DataError("Unrecognized memo type in payment request memo.")

    assert msg.amount is not None

    return await layouts.confirm_payment_request(
        ctx,
        msg.recipient_name,
        format_coin_amount(msg.amount, coin, amount_unit),
        memo_texts,
        coin_shortcut=coin.coin_name,
    )


async def confirm_replacement(
    ctx: wire.Context, description: str, txids: list[bytes]
) -> None:
    await layouts.confirm_replacement(
        ctx,
        description,
        [hexlify(txid).decode() for txid in txids],
    )


async def confirm_modify_output(
    ctx: wire.Context,
    txo: TxOutput,
    orig_txo: TxOutput,
    coin: CoinInfo,
    amount_unit: AmountUnit,
) -> None:
    assert txo.address is not None
    address_short = addresses.address_short(coin, txo.address)
    amount_change = txo.amount - orig_txo.amount
    await layouts.confirm_modify_output(
        ctx,
        address_short,
        amount_change,
        format_coin_amount(abs(amount_change), coin, amount_unit),
        format_coin_amount(txo.amount, coin, amount_unit),
    )


async def confirm_modify_fee(
    ctx: wire.Context,
    user_fee_change: int,
    total_fee_new: int,
    fee_rate: float,
    coin: CoinInfo,
    amount_unit: AmountUnit,
) -> None:
    await layouts.confirm_modify_fee(
        ctx,
        user_fee_change,
        format_coin_amount(abs(user_fee_change), coin, amount_unit),
        format_coin_amount(total_fee_new, coin, amount_unit),
        fee_rate_amount=format_fee_rate(fee_rate, coin) if fee_rate >= 0 else None,
    )


async def confirm_joint_total(
    ctx: wire.Context,
    spending: int,
    total: int,
    coin: CoinInfo,
    amount_unit: AmountUnit,
) -> None:
    await layouts.confirm_joint_total(
        ctx,
        spending_amount=format_coin_amount(spending, coin, amount_unit),
        total_amount=format_coin_amount(total, coin, amount_unit),
        coin_shortcut=coin.coin_name,
    )


async def confirm_total(
    ctx: wire.Context,
    spending: int,
    fee: int,
    fee_rate: float,
    coin: CoinInfo,
    amount_unit: AmountUnit,
) -> None:
    await layouts.confirm_total(
        ctx,
        total_amount=format_coin_amount(spending, coin, amount_unit),
        fee_amount=format_coin_amount(fee, coin, amount_unit),
        amount=format_coin_amount(spending - fee, coin, amount_unit),
        coin_shortcut=coin.coin_name,
        fee_rate_amount=format_fee_rate(fee_rate, coin) if fee_rate > 0 else None,
    )


async def confirm_feeoverthreshold(
    ctx: wire.Context, fee: int, coin: CoinInfo, amount_unit: AmountUnit
) -> None:
    fee_amount = format_coin_amount(fee, coin, amount_unit)
    await layouts.confirm_metadata(
        ctx,
        "fee_over_threshold",
        _(i18n_keys.TITLE__HIGH_FEE),
        _(i18n_keys.SUBTITLE__THE_FEE_IS_UNEXPECTEDLY_HIGH),
        fee_amount,
        ButtonRequestType.FeeOverThreshold,
        description=_(i18n_keys.LIST_KEY__FEE__COLON),
    )


async def confirm_change_count_over_threshold(
    ctx: wire.Context, change_count: int
) -> None:
    await layouts.confirm_metadata(
        ctx,
        "change_count_over_threshold",
        _(i18n_keys.TITLE__WARNING),
        _(i18n_keys.SUBTITLE__THERE_ARE_TOO_MANY_CHANGE_OUTPUTS),
        str(change_count),
        ButtonRequestType.SignTx,
        description=_(i18n_keys.LIST_KEY__CHANGE_COUNT_COLON),
    )


async def confirm_unverified_external_input(ctx: wire.Context) -> None:
    await layouts.confirm_metadata(
        ctx,
        "unverified_external_input",
        "Warning",
        "The transaction contains unverified external inputs.",
        br_code=ButtonRequestType.SignTx,
    )


async def confirm_nondefault_locktime(
    ctx: wire.Context, lock_time: int, lock_time_disabled: bool
) -> None:
    if lock_time_disabled:
        title = _(i18n_keys.TITLE__WARNING)
        text = _(i18n_keys.SUBTITLE__LOCKTIME_IS_SET_BUT_WILL_HAVE_NO_EFFECT)
        param: str | None = None
        description = None
    else:
        title = _(i18n_keys.TITLE__CONFIRM_LOCKTIME)
        text = _(i18n_keys.SUBTITLE__SET_LOCKTIME_FOR_THIS_TRANSACTION)
        if lock_time < _LOCKTIME_TIMESTAMP_MIN_VALUE:
            param = str(lock_time)
            description = _(i18n_keys.LIST_KEY__BLOCK_HEIGHT_COLON)
        else:
            param = format_timestamp(lock_time)
            description = _(i18n_keys.LIST_KEY__TIME_COLON)

    await layouts.confirm_metadata(
        ctx,
        "nondefault_locktime",
        title,
        text,
        param,
        br_code=ButtonRequestType.SignTx,
        description=description,
    )


async def confirm_op_return(
    ctx: wire.Context, data: bytes, amount: int, coin: CoinInfo
) -> None:
    amount_params = (
        {
            "subtitle": _(i18n_keys.TITLE__OP_RETURN_DESC),
            "item_key": _(i18n_keys.LIST_KEY__AMOUNT),
            "item_value": format_coin_amount(amount, coin, AmountUnit.BITCOIN),
        }
        if amount != 0
        else {}
    )

    await layouts.confirm_blob(
        ctx,
        "op_return",
        title="OP_RETURN",
        data=data,
        br_code=ButtonRequestType.ConfirmOutput,
        **amount_params,
    )
