from typing import Sequence
from storage import device
from trezor import wire
from trezor.enums import ButtonRequestType
from trezor.lvglui.i18n import gettext as _, keys as i18n_keys
from trezor.lvglui.scrs.template import ShowSpeed, Turbo
from trezor.strings import strip_amount

from .common import interact, raise_if_cancelled


async def confirm_total_ethereum(
    ctx: wire.GenericContext,
    amount: str,
    gas_price: str | None,
    fee_max: str,
    from_address: str | None,
    to_address: str | None,
    total_amount: str | None,
    contract_addr: str | None = None,
    token_id: int | None = None,
    evm_chain_id: int | None = None,
    raw_data: bytes | None = None,
) -> None:
    from trezor.lvglui.scrs.template import TransactionDetailsETH

    short_amount, striped = strip_amount(amount)
    screen = Turbo()
    # screen = ShowSpeed()
    # screen = TransactionDetailsETH(
    #     _(i18n_keys.TITLE__SEND_MULTILINE).format(short_amount),
    #     from_address,
    #     to_address,
    #     amount,
    #     fee_max,
    #     gas_price=gas_price,
    #     total_amount=total_amount,
    #     primary_color=ctx.primary_color,
    #     contract_addr=contract_addr,
    #     token_id=str(token_id),
    #     evm_chain_id=evm_chain_id,
    #     raw_data=raw_data,
    #     sub_icon_path=ctx.icon_path,
    #     striped=striped,
    # )
    await raise_if_cancelled(
        interact(ctx, screen, "confirm_total", ButtonRequestType.SignTx)
    )


async def confirm_total_ethereum_eip1559(
    ctx: wire.GenericContext,
    amount: str,
    max_priority_fee_per_gas,
    max_fee_per_gas,
    fee_max: str,
    from_address: str | None,
    to_address: str | None,
    total_amount: str | None,
    contract_addr: str | None,
    token_id: int | None,
    evm_chain_id: int | None,
    raw_data: bytes | None,
) -> None:
    from trezor.lvglui.scrs.template import TransactionDetailsETH

    short_amount, striped = strip_amount(amount)
    if device.is_turbomode_enabled():
        screen = Turbo()
    # screen = ShowRipple()
    # screen = ShowLine()
    # screen = ShowBar()
    # screen = ShowLoader()
    # screen = ShowMeter()
    # screen = ShowSpeed(
    #     _(i18n_keys.TITLE__SEND_MULTILINE).format(short_amount),
    #     from_address,
    #     to_address,
    #     amount,
    #     fee_max,
    #     is_eip1559=True,
    #     max_fee_per_gas=max_fee_per_gas,
    #     max_priority_fee_per_gas=max_priority_fee_per_gas,
    #     total_amount=total_amount,
    #     primary_color=ctx.primary_color,
    #     contract_addr=contract_addr,
    #     token_id=str(token_id),
    #     evm_chain_id=evm_chain_id,
    #     raw_data=raw_data,
    #     sub_icon_path=ctx.icon_path,
    #     striped=striped,
    # )
    else:
        screen = TransactionDetailsETH(
            _(i18n_keys.TITLE__SEND_MULTILINE).format(short_amount),
            from_address,
            to_address,
            amount,
            fee_max,
            is_eip1559=True,
            max_fee_per_gas=max_fee_per_gas,
            max_priority_fee_per_gas=max_priority_fee_per_gas,
            total_amount=total_amount,
            primary_color=ctx.primary_color,
            contract_addr=contract_addr,
            token_id=str(token_id),
            evm_chain_id=evm_chain_id,
            raw_data=raw_data,
            sub_icon_path=ctx.icon_path,
            striped=striped,
        )
    await raise_if_cancelled(
        interact(ctx, screen, "confirm_total", ButtonRequestType.SignTx)
    )


async def confirm_total_ripple(
    ctx: wire.GenericContext,
    address: str,
    amount: str,
) -> None:
    from trezor.ui.layouts import confirm_output

    await confirm_output(ctx, address, f"{amount} XRP")


async def confirm_transfer_binance(
    ctx: wire.GenericContext, inputs_outputs: Sequence[tuple[str, str, str]]
) -> None:
    from trezor.lvglui.scrs.template import ConfirmTransferBinance

    screen = ConfirmTransferBinance(inputs_outputs, ctx.primary_color, ctx.icon_path)
    await raise_if_cancelled(
        interact(ctx, screen, "confirm_transfer", ButtonRequestType.ConfirmOutput)
    )


async def confirm_decred_sstx_submission(
    ctx: wire.GenericContext,
    address: str,
    amount: str,
) -> None:
    from trezor.lvglui.scrs.template import ConfirmDecredSstxSubmission

    screen = ConfirmDecredSstxSubmission(
        "Purchase ticket",
        "voting rights",
        amount,
        address,
        primary_color=ctx.primary_color,
    )
    await raise_if_cancelled(
        interact(
            ctx,
            screen,
            "confirm_decred_sstx_submission",
            ButtonRequestType.ConfirmOutput,
        )
    )


async def confirm_total_tron(
    ctx: wire.GenericContext,
    title,
    from_address: str | None,
    to_address: str | None,
    amount: str | None,
    fee_max: str,
    total_amount: str | None,
    striped: bool = False,
) -> None:
    from trezor.lvglui.scrs.template import TransactionDetailsTRON

    screen = TransactionDetailsTRON(
        title,
        from_address,
        to_address,
        amount,
        fee_max,
        primary_color=ctx.primary_color,
        icon_path=ctx.icon_path,
        total_amount=total_amount,
        striped=striped,
    )
    await raise_if_cancelled(
        interact(ctx, screen, "confirm_total", ButtonRequestType.SignTx)
    )


async def confirm_total_ton(
    ctx: wire.GenericContext,
    amount: str,
    gas_price: str | None,
    fee_max: str,
    from_address: str | None,
    to_address: str | None,
    total_amount: str | None,
    contract_addr: str | None = None,
    token_id: int | None = None,
    evm_chain_id: int | None = None,
    raw_data: bytes | None = None,
    is_raw_data: bool = False,
) -> None:
    from trezor.lvglui.scrs.template import TransactionDetailsTON

    short_amount, striped = strip_amount(amount)
    screen = ShowSpeed()

    # screen = TransactionDetailsTON(
    #     _(i18n_keys.TITLE__SEND_MULTILINE).format(short_amount),
    #     from_address,
    #     to_address,
    #     amount,
    #     fee_max,
    #     gas_price=gas_price,
    #     total_amount=total_amount,
    #     primary_color=ctx.primary_color,
    #     contract_addr=contract_addr,
    #     token_id=str(token_id),
    #     evm_chain_id=evm_chain_id,
    #     raw_data=raw_data,
    #     is_raw_data=is_raw_data,
    #     sub_icon_path=ctx.icon_path,
    #     striped=striped,
    # )
    await raise_if_cancelled(
        interact(ctx, screen, "confirm_total", ButtonRequestType.SignTx)
    )


async def confirm_total_alephium(
    ctx: wire.GenericContext,
    amount: str | None = None,
    gas_amount: str | None = None,
    from_address: str | None = None,
    to_address: str | None = None,
    token_id: str | None = None,
    raw_data: bytes | None = None,
    token_amount: str | None = None,
) -> None:
    from trezor.lvglui.scrs.template import TransactionDetailsAlepHium

    subtitle = None
    icon_path = "A:/res/icon-send.png"
    sub_icon_path = ctx.icon_path
    if amount:
        strip_result = strip_amount(amount)
        short_amount = (
            strip_result[0] if isinstance(strip_result, tuple) else strip_result
        )
        title = _(i18n_keys.TITLE__SEND_MULTILINE).format(short_amount)
    elif token_amount:
        short_amount = None
        title = _(i18n_keys.TITLE__SEND_TOKENS)
    elif raw_data:
        title = _(i18n_keys.TITLE__VIEW_TRANSACTION)
        subtitle = _(i18n_keys.CONTENT__FOLLOWING_TRANSACTION_CONTAINS_CONTRACT)
        icon_path = ctx.icon_path
        sub_icon_path = None
    elif gas_amount:
        title = _(i18n_keys.LIST_KEY__TRANSACTION_FEE_COLON)
        icon_path = ctx.icon_path
        sub_icon_path = None

    screen = TransactionDetailsAlepHium(
        title,
        from_address,
        to_address,
        subtitle,
        amount,
        gas_amount=gas_amount,
        primary_color=ctx.primary_color,
        token_id=token_id,
        raw_data=raw_data,
        icon_path=icon_path,
        sub_icon_path=sub_icon_path,
        token_amount=token_amount,
    )
    await raise_if_cancelled(
        interact(ctx, screen, "confirm_total", ButtonRequestType.SignTx)
    )


async def confirm_total_benfen(
    ctx: wire.GenericContext,
    amount: str,
    gas_price: str | None,
    fee_max: str,
    from_address: str | None,
    to_address: str | None,
    total_amount: str | None,
    contract_addr: str | None = None,
    token_id: int | None = None,
    evm_chain_id: int | None = None,
    raw_data: bytes | None = None,
) -> None:
    from trezor.lvglui.scrs.template import TransactionDetailsBenFen

    short_amount, striped = strip_amount(amount)
    screen = TransactionDetailsBenFen(
        _(i18n_keys.TITLE__SEND_MULTILINE).format(short_amount),
        from_address,
        to_address,
        amount,
        fee_max,
        gas_price=gas_price,
        total_amount=total_amount,
        primary_color=ctx.primary_color,
        contract_addr=contract_addr,
        token_id=str(token_id),
        evm_chain_id=evm_chain_id,
        raw_data=raw_data,
        sub_icon_path=ctx.icon_path,
        striped=striped,
    )
    await raise_if_cancelled(
        interact(ctx, screen, "confirm_total", ButtonRequestType.SignTx)
    )
