from typing import TYPE_CHECKING
from ubinascii import hexlify

from trezor import ui, wire
from trezor.enums import ButtonRequestType
from trezor.lvglui.i18n import gettext as _, keys as i18n_keys
from trezor.lvglui.lv_colors import lv_colors

from ...constants.tt import MONO_ADDR_PER_LINE
from .common import button_request, interact, raise_if_cancelled

if TYPE_CHECKING:
    from typing import Any, Awaitable, Iterable, NoReturn, Sequence
    from ..common import PropertyType, ExceptionType


__all__ = (
    "confirm_action",
    "confirm_address",
    "confirm_text",
    "confirm_amount",
    "confirm_reset_device",
    "confirm_backup",
    "confirm_path_warning",
    "confirm_sign_identity",
    "confirm_signverify",
    "show_address",
    "show_address_offline",
    "show_error_and_raise",
    "show_pubkey",
    "show_success",
    "show_lite_card_exit",
    "show_xpub",
    "show_warning",
    "confirm_output",
    "confirm_payment_request",
    "confirm_blob",
    "confirm_properties",
    "confirm_total",
    "confirm_joint_total",
    "confirm_metadata",
    "confirm_replacement",
    "confirm_modify_output",
    "confirm_modify_fee",
    "confirm_coinjoin",
    "show_pairing_error",
    "show_popup",
    "draw_simple_text",
    "request_passphrase_on_device",
    "require_confirm_passphrase",
    "request_pin_on_device",
    "should_show_more",
    "request_strength",
    "confirm_sol_blinding_sign",
    "confirm_sol_transfer",
    "confirm_sol_create_ata",
    "confirm_sol_token_transfer",
    "confirm_sol_memo",
    "confirm_sol_message",
    "confirm_data",
    "confirm_final",
    "confirm_password_input",
    "confirm_blind_sign_common",
    "show_onekey_app_guide",
    "confirm_set_homescreen",
    "confirm_del_wallpaper",
    "confirm_update_res",
    "confirm_domain",
    "request_pin_tips",
    "confirm_remove_nft",
    "confirm_collect_nft",
    "backup_with_keytag",
    "backup_with_lite",
    "confirm_sign_typed_hash",
    "confirm_polkadot_balances",
    "should_show_details",
    "should_show_details_new",
    "should_show_approve_details",
    "show_ur_response",
    "enable_airgap_mode",
    "confirm_nostrmessage",
    "confirm_lnurl_auth",
    "show_error_no_interact",
    "confirm_ton_transfer",
    "confirm_ton_connect",
    "confirm_ton_signverify",
    "confirm_unknown_token_transfer",
    "confirm_neo_token_transfer",
    "confirm_neo_vote",
    "confirm_safe_tx",
    "confirm_safe_approve_hash",
    "confirm_safe_exec_transaction",
)


async def confirm_action(
    ctx: wire.GenericContext,
    br_type: str,
    title: str,
    action: str | None = None,
    description: str | None = None,
    description_param: str | None = None,
    description_param_font: int = ui.BOLD,
    verb: str | None = None,
    verb_cancel: str | None = None,
    hold: bool = False,
    hold_danger: bool = False,
    icon: str | None = "A:/res/warning.png",  # TODO cleanup @ redesign
    icon_color: int | None = None,  # TODO cleanup @ redesign
    reverse: bool = False,  # TODO cleanup @ redesign
    larger_vspace: bool = False,  # TODO cleanup @ redesign
    exc: ExceptionType = wire.ActionCancelled,
    br_code: ButtonRequestType = ButtonRequestType.Other,
    anim_dir: int = 1,
    hold_level: int = 0,
    primary_color=lv_colors.ONEKEY_GREEN,
) -> None:
    from trezor.lvglui.scrs.common import FullSizeWindow

    if description and description_param is not None:
        description = description.format(description_param)
    confirm_screen = FullSizeWindow(
        title,
        f"{description or ''}{' ' + (action or '')}",
        verb if verb else _(i18n_keys.BUTTON__CONFIRM),
        cancel_text=verb_cancel
        if verb_cancel
        else _(i18n_keys.BUTTON__REJECT)
        if hold
        else _(i18n_keys.BUTTON__CANCEL),
        icon_path=icon,
        hold_confirm=hold,
        anim_dir=anim_dir,
        primary_color=primary_color,
    )
    if hold_level:
        confirm_screen.slider.change_knob_style(hold_level)
    await raise_if_cancelled(
        interact(ctx, confirm_screen, br_type, br_code),
        exc,
    )
    if anim_dir == 2:
        from trezor import loop

        await loop.sleep(300)


async def confirm_reset_device(
    ctx: wire.GenericContext, prompt: str, recovery: bool = False
) -> None:
    from trezor.lvglui.scrs.common import FullSizeWindow

    if recovery:
        title = _(i18n_keys.TITLE__IMPORT_WALLET)
        # icon = "A:/res/recovery.png"
    else:
        title = _(i18n_keys.TITLE__CREATE_NEW_WALLET)
        # icon = "A:/res/add.png"
    confirm_text = _(i18n_keys.BUTTON__CONTINUE)
    cancel_text = _(i18n_keys.BUTTON__CANCEL)
    restscreen = FullSizeWindow(
        title, prompt, confirm_text, cancel_text, icon_path=None, anim_dir=0
    )
    await raise_if_cancelled(
        interact(
            ctx,
            restscreen,
            "recover_device" if recovery else "setup_device",
            ButtonRequestType.ProtectCall
            if recovery
            else ButtonRequestType.ResetDevice,
        )
    )


async def request_strength() -> int:
    from trezor.lvglui.scrs.recovery_device import SelectWordCounter

    word_cnt_strength_map = {
        12: 128,
        18: 192,
        24: 256,
    }
    screen = SelectWordCounter(_(i18n_keys.TITLE__READY_TO_CREATE))
    word_cnt = await screen.request()
    if not word_cnt:
        raise wire.ActionCancelled()
    return word_cnt_strength_map[word_cnt]


async def confirm_wipe_device(ctx: wire.GenericContext):
    from trezor.lvglui.scrs.wipe_device import WipeDevice

    confirm_screen = WipeDevice()
    await raise_if_cancelled(
        interact(ctx, confirm_screen, "wipe_device", ButtonRequestType.WipeDevice)
    )


async def confirm_wipe_device_tips(ctx: wire.GenericContext):
    from trezor.lvglui.scrs.wipe_device import WipeDeviceTips

    confirm_screen = WipeDeviceTips()
    await raise_if_cancelled(
        interact(ctx, confirm_screen, "wipe_device", ButtonRequestType.WipeDevice)
    )


async def confirm_wipe_device_success(ctx: wire.GenericContext):
    from trezor.lvglui.scrs.wipe_device import WipeDeviceSuccess

    confirm_screen = WipeDeviceSuccess()
    return await interact(
        ctx, confirm_screen, "wipe_device", ButtonRequestType.WipeDevice
    )


# TODO cleanup @ redesign
async def confirm_backup(ctx: wire.GenericContext) -> bool:
    from trezor.lvglui.scrs.common import FullSizeWindow

    title = _(i18n_keys.TITLE__WALLET_IS_READY)
    subtitle = _(i18n_keys.SUBTITLE__DEVICE_SETUP_WALLET_IS_READY)
    confirm_text = _(i18n_keys.BUTTON__CONTINUE)
    cancel_text = _(i18n_keys.BUTTON__SKIP)
    icon = "A:/res/success.png"
    if ctx == wire.DUMMY_CONTEXT:
        cancel_text = ""
    screen = FullSizeWindow(title, subtitle, confirm_text, cancel_text, icon_path=icon)
    confirmed = await interact(
        ctx,
        screen,
        "backup_device",
        ButtonRequestType.ResetDevice,
    )
    if confirmed:
        return True

    title = _(i18n_keys.TITLE__WARNING)
    subtitle = _(i18n_keys.SUBTITLE__DEVICE_SETUP_SKIP_BACK_UP_WARNING)
    icon = "A:/res/warning.png"
    screen = FullSizeWindow(title, subtitle, confirm_text, cancel_text, icon_path=icon)
    confirmed = await interact(
        ctx,
        screen,
        "backup_device",
        ButtonRequestType.ResetDevice,
    )
    return bool(confirmed)


async def confirm_path_warning(
    ctx: wire.GenericContext, path: str, path_type: str = "Path"
) -> None:
    from trezor.lvglui.scrs.common import FullSizeWindow

    screen = FullSizeWindow(
        _(i18n_keys.TITLE__UNKNOWN_PATH),
        _(i18n_keys.SUBTITLE__BTC_GET_ADDRESS_UNKNOWN_PATH).format(path),
        _(i18n_keys.BUTTON__CONFIRM),
        _(i18n_keys.BUTTON__CANCEL),
        icon_path="A:/res/warning.png",
    )
    screen.btn_yes.enable(bg_color=lv_colors.ONEKEY_YELLOW, text_color=lv_colors.BLACK)
    await raise_if_cancelled(
        interact(
            ctx,
            screen,
            "path_warning",
            ButtonRequestType.UnknownDerivationPath,
        )
    )


async def show_xpub(
    ctx: wire.GenericContext,
    xpub: str,
    title: str = "",
    cancel: str = "",
    path: str = "",
    network: str = "BTC",
) -> None:
    from trezor.lvglui.scrs.template import XpubOrPub

    await raise_if_cancelled(
        interact(
            ctx,
            XpubOrPub(
                _(i18n_keys.TITLE__STR_PUBLIC_KEY).format(network),
                path=path,
                primary_color=ctx.primary_color,
                icon_path=ctx.icon_path,
                xpub=xpub,
            ),
            "show_pubkey",
            ButtonRequestType.PublicKey,
        )
    )


async def show_address(
    ctx: wire.GenericContext,
    address: str,
    *,
    address_qr: str | None = None,
    case_sensitive: bool = True,
    address_n: str | None,
    network: str = "",
    multisig_index: int | None = None,
    xpubs: Sequence[str] = (),
    address_extra: str | None = None,
    title_qr: str | None = None,
    evm_chain_id: int | None = None,
    title: str = "",
    addr_type: str | None = None,
) -> None:
    is_multisig = len(xpubs) > 0
    from trezor.lvglui.scrs.template import Address

    by_qr = isinstance(ctx, wire.QRContext)
    if is_multisig:
        return await interact(
            ctx,
            Address(
                title,
                address_n,
                address,
                ctx.primary_color,
                ctx.icon_path,
                xpubs,
                address_qr,
                multisig_index,
                qr_first=by_qr,
            ),
            "show_address",
            ButtonRequestType.Address,
        )
    await interact(
        ctx,
        Address(
            title if title else _(i18n_keys.TITLE__STR_ADDRESS).format(network),
            address_n,
            address,
            ctx.primary_color,
            ctx.icon_path,
            address_qr=address_qr,
            addr_type=addr_type,
            evm_chain_id=evm_chain_id,
            qr_first=by_qr,
        ),
        "show_address",
        ButtonRequestType.Address,
    )
    from trezor import loop

    await loop.sleep(300)


async def show_address_offline(
    ctx: wire.GenericContext,
    address: str,
    *,
    address_qr: str | None = None,
    case_sensitive: bool = True,
    network: str = "",
    multisig_index: int | None = None,
    xpubs: Sequence[str] = (),
    address_extra: str | None = None,
    title_qr: str | None = None,
    evm_chain_id: int | None = None,
    title: str = "",
    addr_type: str | None = None,
    prev_scr=None,
    account_name: str = "",
) -> None:
    is_multisig = len(xpubs) > 0
    from trezor.lvglui.scrs.template import AddressOffline

    by_qr = isinstance(ctx, wire.QRContext)
    if is_multisig:
        return await interact(
            ctx,
            AddressOffline(
                title,
                address,
                ctx.primary_color,
                ctx.icon_path,
                xpubs,
                address_qr,
                multisig_index,
                qr_first=by_qr,
                network=network,
            ),
            "show_address",
            ButtonRequestType.Address,
        )
    res = await interact(
        ctx,
        AddressOffline(
            title if title else _(i18n_keys.TITLE__STR_ADDRESS).format(network),
            address,
            ctx.primary_color,
            ctx.icon_path,
            address_qr=address_qr,
            addr_type=addr_type,
            evm_chain_id=evm_chain_id,
            qr_first=by_qr,
            network=network,
            prev_scr=prev_scr,
            account_name=account_name,
        ),
        "show_address",
        ButtonRequestType.Address,
    )
    from trezor import loop

    await loop.sleep(50)
    return res


async def show_pubkey(
    ctx: wire.Context,
    pubkey: str,
    title: str = "Confirm public key",
    network: str = "ETH",
    path: str = "",
) -> None:
    from trezor.lvglui.scrs.template import XpubOrPub

    await raise_if_cancelled(
        interact(
            ctx,
            XpubOrPub(
                _(i18n_keys.TITLE__STR_PUBLIC_KEY).format(network),
                path=path,
                pubkey=pubkey,
                primary_color=ctx.primary_color,
                icon_path=ctx.icon_path,
            ),
            "show_pubkey",
            ButtonRequestType.PublicKey,
        )
    )


async def _show_modal(
    ctx: wire.GenericContext,
    br_type: str,
    br_code: ButtonRequestType,
    header: str,
    subheader: str | None,
    content: str,
    button_confirm: str | None,
    button_cancel: str | None,
    icon: str,
    icon_color: int,
    btn_yes_bg_color=None,
    exc: ExceptionType = wire.ActionCancelled,
) -> None:
    from trezor.lvglui.scrs.template import Modal

    screen = Modal(
        header,
        content,
        confirm_text=button_confirm,
        cancel_text=button_cancel,
        icon_path=icon,
    )
    if btn_yes_bg_color:
        screen.btn_yes.enable(bg_color=btn_yes_bg_color or lv_colors.ONEKEY_GREEN)
    await raise_if_cancelled(
        interact(
            ctx,
            screen,
            br_type,
            br_code,
        ),
        exc,
    )


async def show_error_and_raise(
    ctx: wire.GenericContext,
    br_type: str,
    content: str,
    header: str = "Error",
    subheader: str | None = None,
    button: str | None = None,
    red: bool = False,
    exc: ExceptionType = wire.ActionCancelled,
) -> NoReturn:
    await _show_modal(
        ctx,
        br_type=br_type,
        br_code=ButtonRequestType.Other,
        header=header,
        subheader=subheader,
        content=content,
        button_confirm=None,
        button_cancel=button if button else _(i18n_keys.BUTTON__CLOSE),
        icon="A:/res/danger.png",
        icon_color=ui.RED if red else ui.ORANGE_ICON,
        exc=exc,
    )
    raise exc


def show_warning(
    ctx: wire.GenericContext,
    br_type: str,
    content: str,
    header: str = "Warning",
    subheader: str | None = None,
    button: str | None = None,
    br_code: ButtonRequestType = ButtonRequestType.Warning,
    icon: str = "A:/res/warning.png",
    icon_color: int = ui.RED,
    btn_yes_bg_color=None,
) -> Awaitable[None]:
    return _show_modal(
        ctx,
        br_type=br_type,
        br_code=br_code,
        header=header,
        subheader=subheader,
        content=content,
        button_confirm=button if button else _(i18n_keys.BUTTON__TRY_AGAIN),
        button_cancel=None,
        icon=icon,
        icon_color=icon_color,
        btn_yes_bg_color=btn_yes_bg_color,
    )


def show_success(
    ctx: wire.GenericContext,
    br_type: str,
    content: str,
    header: str = "Success",
    subheader: str | None = None,
    button: str = "Done",
) -> Awaitable[None]:
    return _show_modal(
        ctx,
        br_type=br_type,
        br_code=ButtonRequestType.Success,
        header=header,
        subheader=subheader,
        content=content,
        button_confirm=button,
        button_cancel=None,
        icon="A:/res/success.png",
        icon_color=ui.GREEN,
    )


async def show_lite_card_exit(
    ctx: wire.GenericContext,
    content: str,
    header: str = "Success",
    subheader: str | None = None,
    button_confirm: str = "Exit",
    button_cancel: str = "Cancel",
) -> None:
    from trezor.lvglui.scrs.template import Modal

    screen = Modal(
        header,
        content,
        confirm_text=button_confirm,
        cancel_text=button_cancel,
        icon_path=None,
    )
    screen.btn_yes.enable(bg_color=lv_colors.ONEKEY_RED_1, text_color=lv_colors.BLACK)
    await raise_if_cancelled(
        interact(
            ctx,
            screen,
            "show_lite_card_exit",
            ButtonRequestType.Success,
        ),
        wire.ActionCancelled,
    )


async def show_error_no_interact(title: str, subtitle: str, cancel_text: str = ""):
    from trezor.lvglui.scrs.template import ErrorFeedback

    screen = ErrorFeedback(
        title,
        subtitle,
        cancel_text,
    )
    await screen.request()


async def confirm_output(
    ctx: wire.GenericContext,
    address: str,
    amount: str,
    font_amount: int = ui.NORMAL,  # TODO cleanup @ redesign
    title: str = "Confirm Transaction",
    subtitle: str | None = None,
    color_to: int = ui.FG,  # TODO cleanup @ redesign
    to_str: str = " to\n",  # TODO cleanup @ redesign
    to_paginated: bool = False,  # TODO cleanup @ redesign
    width: int = MONO_ADDR_PER_LINE,
    width_paginated: int = MONO_ADDR_PER_LINE - 1,
    br_code: ButtonRequestType = ButtonRequestType.ConfirmOutput,
    icon: str = ui.ICON_SEND,
) -> None:
    from trezor.lvglui.scrs.template import TransactionOverview
    from trezor.strings import strip_amount

    await raise_if_cancelled(
        interact(
            ctx,
            TransactionOverview(
                _(i18n_keys.TITLE__SEND_MULTILINE).format(strip_amount(amount)[0]),
                address,
                primary_color=ctx.primary_color,
                icon_path=ctx.icon_path,
            ),
            "confirm_output",
            br_code,
        )
    )


async def should_show_details(
    ctx: wire.GenericContext,
    address: str,
    title: str,
    br_code: ButtonRequestType = ButtonRequestType.ConfirmOutput,
) -> bool:
    from trezor.lvglui.scrs.template import TransactionOverview

    res = await interact(
        ctx,
        TransactionOverview(
            title,
            address=address,
            primary_color=ctx.primary_color,
            icon_path=ctx.icon_path,
            has_details=True,
        ),
        "confirm_output",
        br_code,
    )
    if not res:
        from trezor import loop

        await loop.sleep(300)
        raise wire.ActionCancelled()
    elif res == 2:  # show more
        return True
    else:  # confirm
        return False


async def should_show_details_new(
    ctx: wire.GenericContext,
    title: str,
    br_code: ButtonRequestType = ButtonRequestType.ConfirmOutput,
    **kwargs,
) -> bool:
    from trezor.lvglui.scrs.template import TransactionOverviewNew

    res = await interact(
        ctx,
        TransactionOverviewNew(
            title,
            primary_color=ctx.primary_color,
            icon_path=ctx.icon_path,
            has_details=True,
            **kwargs,
        ),
        "confirm_output",
        br_code,
    )
    if not res:
        from trezor import loop

        await loop.sleep(300)
        raise wire.ActionCancelled()
    elif res == 2:  # show more
        return True
    else:  # confirm
        return False


async def should_show_approve_details(
    ctx: wire.GenericContext,
    approve_spender: str,
    max_fee: str | None,
    token_address: str,
    provider_icon_path: str | None,
    title: str,
    is_unlimited: bool = False,
    br_code: ButtonRequestType = ButtonRequestType.ConfirmOutput,
) -> bool:
    from trezor.lvglui.scrs.template import ApproveErc20ETHOverview

    res = await interact(
        ctx,
        ApproveErc20ETHOverview(
            title,
            approve_spender,
            max_fee,
            token_address,
            primary_color=ctx.primary_color,
            icon_path=provider_icon_path,
            sub_icon_path=ctx.icon_path,
            has_details=True,
            is_unlimited=is_unlimited,
        ),
        "approve_erc20_eth",
        br_code,
    )
    if not res:
        from trezor import loop

        await loop.sleep(300)
        raise wire.ActionCancelled()
    elif res == 2:  # show more
        return True
    else:  # confirm
        return False


async def confirm_payment_request(
    ctx: wire.GenericContext,
    recipient_name: str,
    amount: str,
    memos: list[str],
    coin_shortcut: str,
) -> Any:
    from trezor.lvglui.scrs.template import ConfirmPaymentRequest

    subtitle = " ".join(memos)
    screen = ConfirmPaymentRequest(
        _(i18n_keys.TITLE__CONFIRM_PAYMENT).format(coin_shortcut),
        subtitle,
        amount,
        recipient_name,
        primary_color=ctx.primary_color,
    )
    return await raise_if_cancelled(
        interact(
            ctx, screen, "confirm_payment_request", ButtonRequestType.ConfirmOutput
        )
    )


async def should_show_more(
    ctx: wire.GenericContext,
    title: str,
    para: Iterable[tuple[int, str]],
    button_text: str = "Show all",
    br_type: str = "should_show_more",
    br_code: ButtonRequestType = ButtonRequestType.Other,
    icon: str = ui.ICON_DEFAULT,
    icon_color: int = ui.ORANGE_ICON,
) -> bool:
    """Return True always because we have larger screen"""
    from trezor.lvglui.scrs.template import ShouldShowMore
    from .common import CONFIRM, SHOW_MORE

    contents = []
    for _i, text in para:
        contents.append(text)
    show_more = ShouldShowMore(
        title,
        contents[0],
        "\n".join(contents[1:]),
        button_text,
        primary_color=ctx.primary_color,
    )
    result = await raise_if_cancelled(interact(ctx, show_more, br_type, br_code))
    assert result in (CONFIRM, SHOW_MORE)

    return result == SHOW_MORE


async def confirm_blob(
    ctx: wire.GenericContext,
    br_type: str,
    title: str,
    data: bytes | str,
    description: str | None = None,
    hold: bool = False,
    br_code: ButtonRequestType = ButtonRequestType.Other,
    icon: str | None = "A:/res/warning.png",  # TODO cleanup @ redesign
    icon_color: int = ui.GREEN,  # TODO cleanup @ redesign
    ask_pagination: bool = False,
    subtitle: str | None = None,
    item_key: str | None = None,
    item_value: str | None = None,
) -> None:
    """Confirm data blob.

    Applicable for public keys, signatures, hashes. In general, any kind of
    data that is not human-readable, and can be wrapped at any character.

    For addresses, use `confirm_address`.

    Displays in monospace font. Paginates automatically.
    If data is provided as bytes or bytearray, it is converted to hex.
    """
    from trezor.lvglui.scrs.template import BlobDisPlay

    if isinstance(data, (bytes, bytearray)):
        from trezor import strings

        data_str = strings.format_customer_data(data)
    else:
        data_str = data
    blob = BlobDisPlay(
        title,
        description if description is not None else "",
        data_str,
        icon_path=icon,
        primary_color=ctx.primary_color,
        subtitle=subtitle,
        item_key=item_key,
        item_value=item_value,
    )
    return await raise_if_cancelled(interact(ctx, blob, br_type, br_code))


async def confirm_data(
    ctx: wire.GenericContext,
    br_type: str,
    title: str,
    data: bytes | str | bytearray,
    description: str | None = None,
    br_code: ButtonRequestType = ButtonRequestType.Other,
) -> None:
    from trezor.lvglui.scrs.template import ContractDataOverview

    if isinstance(data, (bytes, bytearray)):
        if len(data) > 1024:
            data_str = hexlify(data).decode()
        else:
            data_str = "0x" + hexlify(data).decode()
    else:
        data_str = data
    return await raise_if_cancelled(
        interact(
            ctx,
            ContractDataOverview(
                title, description, data_str, primary_color=ctx.primary_color
            ),
            br_type,
            br_code,
        )
    )


def confirm_address(
    ctx: wire.GenericContext,
    title: str,
    address: str,
    description: str | None = "Address:",
    br_type: str = "confirm_address",
    br_code: ButtonRequestType = ButtonRequestType.Other,
    icon: str = ui.ICON_SEND,  # TODO cleanup @ redesign
    icon_color: int = ui.GREEN,  # TODO cleanup @ redesign
) -> Awaitable[None]:
    # TODO clarify API - this should be pretty limited to support mainly confirming
    # destinations and similar
    return confirm_blob(
        ctx,
        br_type=br_type,
        title=title,
        data=address,
        description=description,
        br_code=br_code,
        icon=icon,
        icon_color=icon_color,
    )


async def confirm_text(
    ctx: wire.GenericContext,
    br_type: str,
    title: str,
    data: str,
    description: str | None = None,
    br_code: ButtonRequestType = ButtonRequestType.Other,
    icon: str | None = "A:/res/warning.png",  # TODO cleanup @ redesign
    icon_color: int = ui.GREEN,  # TODO cleanup @ redesign
) -> None:
    """Confirm textual data.

    Applicable for human-readable strings, numbers, date/time values etc.

    For amounts, use `confirm_amount`.

    Displays in bold font. Paginates automatically.
    """
    from trezor.lvglui.scrs.template import BlobDisPlay

    screen = BlobDisPlay(
        title, description, data, icon_path=icon, primary_color=ctx.primary_color
    )
    await raise_if_cancelled(interact(ctx, screen, br_type, br_code))


def confirm_amount(
    ctx: wire.GenericContext,
    title: str,
    amount: str,
    description: str = "Amount:",
    br_type: str = "confirm_amount",
    br_code: ButtonRequestType = ButtonRequestType.Other,
    icon: str = ui.ICON_SEND,  # TODO cleanup @ redesign
    icon_color: int = ui.GREEN,  # TODO cleanup @ redesign
) -> Awaitable[None]:
    """Confirm amount."""
    # TODO clarify API - this should be pretty limited to support mainly confirming
    # destinations and similar
    return confirm_text(
        ctx,
        br_type=br_type,
        title=title,
        data=amount,
        description=_(i18n_keys.LIST_KEY__AMOUNT__COLON),
        br_code=br_code,
        icon=icon,
        icon_color=icon_color,
    )


# TODO keep name and value on the same page if possible
async def confirm_properties(
    ctx: wire.GenericContext,
    br_type: str,
    title: str,
    props: Iterable[PropertyType],
    icon: str = ui.ICON_SEND,  # TODO cleanup @ redesign
    icon_color: int = ui.GREEN,  # TODO cleanup @ redesign
    hold: bool = False,
    br_code: ButtonRequestType = ButtonRequestType.ConfirmOutput,
) -> None:
    para = []
    from trezor.lvglui.scrs.template import ConfirmProperties

    for key, val in props:
        if key and val:
            if isinstance(val, str):
                para.append((key, val))
            elif isinstance(val, bytes):
                para.append((key, hexlify(val).decode()))
    screen = ConfirmProperties(title, para, ctx.primary_color)
    await raise_if_cancelled(interact(ctx, screen, br_type, br_code))


async def confirm_total(
    ctx: wire.GenericContext,
    total_amount: str,
    fee_amount: str,
    amount: str,
    title: str = "Confirm transaction",
    total_label: str = "Total amount:\n",
    fee_label: str = "\nincluding fee:\n",
    icon_color: int = ui.GREEN,
    br_type: str = "confirm_total",
    br_code: ButtonRequestType = ButtonRequestType.SignTx,
    coin_shortcut: str = "BTC",
    fee_rate_amount: str | None = None,
) -> None:
    from trezor.lvglui.scrs.template import TransactionDetailsBTC
    from trezor.strings import strip_amount

    striped_amount, striped = strip_amount(amount)
    screen = TransactionDetailsBTC(
        _(i18n_keys.TITLE__SEND_MULTILINE).format(striped_amount),
        amount,
        fee_amount,
        total_amount,
        primary_color=ctx.primary_color,
        icon_path=ctx.icon_path,
        striped=striped,
    )
    await raise_if_cancelled(interact(ctx, screen, br_type, br_code))


async def confirm_joint_total(
    ctx: wire.GenericContext,
    spending_amount: str,
    total_amount: str,
    coin_shortcut: str = "BTC",
) -> None:
    from trezor.lvglui.scrs.template import JointTransactionDetailsBTC

    screen = JointTransactionDetailsBTC(
        _(i18n_keys.TITLE__SIGN_STR_JOINT_TX).format(coin_shortcut),
        spending_amount,
        total_amount,
        primary_color=ctx.primary_color,
    )
    await raise_if_cancelled(
        interact(ctx, screen, "confirm_joint_total", ButtonRequestType.SignTx)
    )


async def confirm_metadata(
    ctx: wire.GenericContext,
    br_type: str,
    title: str,
    content: str,
    param: str | None = None,
    br_code: ButtonRequestType = ButtonRequestType.SignTx,
    description: str | None = None,
    hide_continue: bool = False,
    hold: bool = False,
    icon: str | None = None,
    icon_color: int | None = None,
) -> None:
    from trezor.lvglui.scrs.template import ConfirmMetaData

    has_icon_path = hasattr(ctx, "icon_path")
    confirm = ConfirmMetaData(
        title,
        content,
        description,
        param,
        ctx.primary_color,
        ctx.icon_path if has_icon_path is True else None,
    )
    await raise_if_cancelled(interact(ctx, confirm, br_type, br_code))


async def confirm_replacement(
    ctx: wire.GenericContext, description: str, txids: list[str]
) -> None:
    from trezor.lvglui.scrs.template import ConfirmReplacement

    screen = ConfirmReplacement(description, txids, ctx.primary_color)
    await raise_if_cancelled(
        interact(ctx, screen, "confirm_replacement", ButtonRequestType.SignTx)
    )


async def confirm_modify_output(
    ctx: wire.GenericContext,
    address: str,
    sign: int,
    amount_change: str,
    amount_new: str,
) -> None:
    if sign < 0:
        description = _(i18n_keys.LIST_KEY__INCREASED_BY__COLON)
    else:
        description = _(i18n_keys.LIST_KEY__DECREASED_BY__COLON)
    from trezor.lvglui.scrs.template import ModifyOutput

    screen = ModifyOutput(
        address, description, amount_change, amount_new, primary_Color=ctx.primary_color
    )
    await raise_if_cancelled(
        interact(
            ctx,
            screen,
            "modify_output",
            ButtonRequestType.ConfirmOutput,
        )
    )


async def confirm_modify_fee(
    ctx: wire.GenericContext,
    sign: int,
    user_fee_change: str,
    total_fee_new: str,
    fee_rate_amount: str | None = None,
) -> None:
    if sign == 0:
        description = _(i18n_keys.LIST_KEY__NO_CHANGE__COLON)
    else:
        if sign < 0:
            description = _(i18n_keys.LIST_KEY__DECREASED_BY__COLON)
        else:
            description = _(i18n_keys.LIST_KEY__INCREASED_BY__COLON)

    from trezor.lvglui.scrs.template import ModifyFee

    screen = ModifyFee(description, user_fee_change, total_fee_new, ctx.primary_color)
    await raise_if_cancelled(
        interact(ctx, screen, "modify_fee", ButtonRequestType.SignTx)
    )


async def confirm_coinjoin(
    ctx: wire.GenericContext, coin_name: str, max_rounds: int, max_fee_per_vbyte: str
) -> None:
    title = _(i18n_keys.TITLE__AUTHORIZE_COINJOIN)
    from trezor.lvglui.scrs.template import ConfirmCoinJoin

    screen = ConfirmCoinJoin(
        title,
        coin_name,
        str(max_rounds),
        max_fee_per_vbyte,
        ctx.primary_color,
    )
    await raise_if_cancelled(
        interact(ctx, screen, "coinjoin_final", ButtonRequestType.Other)
    )


# TODO cleanup @ redesign
async def confirm_sign_identity(
    ctx: wire.GenericContext, proto: str, identity: str, challenge_visual: str | None
) -> None:
    from trezor.lvglui.scrs.template import ConfirmSignIdentity

    screen = ConfirmSignIdentity(
        f"Sign {proto}",
        identity,
        subtitle=challenge_visual,
        primary_color=ctx.primary_color,
    )
    await raise_if_cancelled(
        interact(ctx, screen, "sign_identity", ButtonRequestType.Other)
    )


async def confirm_signverify(
    ctx: wire.GenericContext,
    coin: str,
    message: str,
    address: str,
    verify: bool,
    evm_chain_id: int | None = None,
    is_standard: bool = True,
) -> None:
    if verify:
        header = _(i18n_keys.TITLE__VERIFY_STR_MESSAGE).format(coin)
        br_type = "verify_message"
    else:
        header = _(i18n_keys.TITLE__SIGN_STR_MESSAGE).format(coin)
        br_type = "sign_message"
    from trezor.lvglui.scrs.template import Message

    await raise_if_cancelled(
        interact(
            ctx,
            Message(
                header,
                address,
                message,
                ctx.primary_color,
                ctx.icon_path,
                verify,
                evm_chain_id,
                is_standard=is_standard,
            ),
            br_type,
            ButtonRequestType.Other,
        )
    )


async def show_popup(
    title: str,
    description: str | None = None,
    subtitle: str | None = None,
    description_param: str = "",
    timeout_ms: int = 3000,
    icon: str | None = None,
) -> None:
    from trezor.lvglui.scrs.common import FullSizeWindow
    from trezor import loop

    if description and description_param:
        description = description.format(description_param)
    subtitle = f"{subtitle or ''} {description or ''}"
    FullSizeWindow(
        title, subtitle, icon_path=icon, auto_close_ms=timeout_ms, anim_dir=0
    )
    await loop.sleep(500)


def draw_simple_text(
    title: str,
    description: str = "",
    icon_path: str | None = "A:/res/warning.png",
    auto_close_ms: int = 2000,
) -> None:
    from trezor.lvglui.scrs.common import FullSizeWindow

    FullSizeWindow(
        title, description, icon_path=icon_path, auto_close_ms=auto_close_ms, anim_dir=0
    )


async def request_passphrase_on_device(
    ctx: wire.GenericContext, max_len: int, result: str | None = None, min_len: int = 0
) -> str:
    await button_request(
        ctx, "passphrase_device", code=ButtonRequestType.PassphraseEntry
    )
    from trezor.lvglui.scrs.passphrase import PassphraseRequest

    while True:
        screen = PassphraseRequest(max_len, result, min_len)
        result = await ctx.wait(screen.request())
        if result is None and min_len == 1:
            return None
        if result is None:
            raise wire.ActionCancelled("Passphrase entry cancelled")

        assert isinstance(result, str)

        if await require_confirm_passphrase(ctx, result, from_device=True):
            break
    return result


async def require_confirm_passphrase(
    ctx: wire.GenericContext, passphrase: str, from_device: bool = False
) -> bool:
    from trezor.lvglui.scrs.template import PassphraseDisplayConfirm

    screen = PassphraseDisplayConfirm(passphrase, from_device)
    return bool(await ctx.wait(screen.request()))


async def request_pin_on_device(
    ctx: wire.GenericContext,
    prompt: str,
    attempts_remaining: int | None,
    allow_cancel: bool,
    allow_fingerprint: bool,
    close_others: bool = True,
    standy_wall_only: bool = False,
    attach_wall_only: bool = False,
) -> str:

    if not attach_wall_only:
        await button_request(
            ctx,
            "pin_device",
            code=ButtonRequestType.PinEntry,
            close_others=close_others,
        )
    else:
        await button_request(
            ctx,
            "pin_device",
            code=ButtonRequestType.AttachPin,
            close_others=close_others,
        )
    from storage import device

    if attempts_remaining is None or attempts_remaining == device.PIN_MAX_ATTEMPTS:
        from apps.common import passphrase

        if standy_wall_only and passphrase.is_passphrase_pin_enabled():
            subprompt = f"{_(i18n_keys.CONTENT__PIN_FOR_STANDARD_WALLET)}"
        else:
            subprompt = ""
    elif attempts_remaining == 2:
        await confirm_password_input(ctx)
        subprompt = f"{_(i18n_keys.MSG__INCORRECT_PIN_STR_ATTEMPTS_LEFT).format(attempts_remaining)}"
    elif attempts_remaining == 1:
        subprompt = f"{_(i18n_keys.MSG__INCORRECT_PIN_THIS_IS_YOUR_LAST_ATTEMPT)}"
    else:
        subprompt = f"{_(i18n_keys.MSG__INCORRECT_PIN_STR_ATTEMPTS_LEFT).format(attempts_remaining)}"
    from trezor.lvglui.scrs.pinscreen import InputPin

    min_len = 4
    if attach_wall_only:
        min_len = 6
    else:
        min_len = 4
    pinscreen = InputPin(
        title=prompt,
        subtitle=subprompt,
        allow_fingerprint=allow_fingerprint,
        standy_wall_only=standy_wall_only,
        min_len=min_len,
    )
    if subprompt:
        from trezor import motor

        motor.vibrate(motor.ERROR)
    result = await ctx.wait(pinscreen.request())
    if not result:
        if not allow_cancel:
            from trezor import loop

            loop.clear()
        raise wire.PinCancelled
    assert isinstance(result, str)
    return result


async def request_pin_tips(ctx: wire.GenericContext) -> None:
    from trezor.lvglui.scrs.pinscreen import PinTip

    tipscreen = PinTip()
    await raise_if_cancelled(
        interact(ctx, tipscreen, "set_pin", ButtonRequestType.Other)
    )


async def show_pairing_error() -> None:
    await show_popup(
        _(i18n_keys.TITLE__PAIR_FAILED),
        description=None,
        subtitle=_(i18n_keys.SUBTITLE__BLUETOOTH_PAIR_PAIR_FAILED),
        timeout_ms=2000,
        icon="A:/res/danger.png",
    )


async def confirm_domain(ctx: wire.GenericContext, **kwargs) -> None:
    from trezor.lvglui.scrs.template import EIP712DOMAIN

    screen = EIP712DOMAIN(
        _(i18n_keys.TITLE__STR_TYPED_DATA).format(ctx.name),
        primary_color=ctx.primary_color,
        icon_path=ctx.icon_path,
        **kwargs,
    )
    await raise_if_cancelled(
        interact(ctx, screen, "confirm_domain", ButtonRequestType.ProtectCall)
    )


async def confirm_eip712_warning(
    ctx: wire.GenericContext, primary_type: str, warning_level: int, text: str
) -> None:
    from trezor.lvglui.scrs.template import EIP712Warning

    screen = EIP712Warning(
        _(i18n_keys.TITLE__STR_TYPED_DATA).format(ctx.name),
        warning_level,
        text,
        primary_type,
        ctx.primary_color,
        ctx.icon_path,
    )
    await raise_if_cancelled(
        interact(ctx, screen, "confirm_eip712_warning", ButtonRequestType.ProtectCall)
    )


async def confirm_security_check(ctx: wire.GenericContext) -> None:
    from trezor.lvglui.scrs.template import SecurityCheck

    screen = SecurityCheck()
    await raise_if_cancelled(
        interact(ctx, screen, "security_check", ButtonRequestType.ProtectCall)
    )


async def confirm_sol_blinding_sign(
    ctx: wire.GenericContext, fee_payer: str, message_hex: str
) -> None:
    from trezor.lvglui.scrs.template import SolBlindingSign

    screen = SolBlindingSign(fee_payer, message_hex, ctx.primary_color, ctx.icon_path)
    await raise_if_cancelled(
        interact(ctx, screen, "sol_blinding_sign", ButtonRequestType.ProtectCall)
    )


async def confirm_sol_transfer(
    ctx: wire.GenericContext, from_addr: str, to_addr: str, fee_payer: str, amount: str
) -> None:
    from trezor.strings import strip_amount

    striped_amount, striped = strip_amount(amount)
    title = _(i18n_keys.TITLE__SEND_MULTILINE).format(striped_amount)
    if should_show_details(ctx, to_addr, title):
        from trezor.lvglui.scrs.template import SolTransfer

        screen = SolTransfer(
            title,
            from_addr=from_addr,
            to_addr=to_addr,
            fee_payer=fee_payer,
            amount=amount,
            primary_color=ctx.primary_color,
            icon_path=ctx.icon_path,
            striped=striped,
        )
        await raise_if_cancelled(
            interact(ctx, screen, "sol_transfer", ButtonRequestType.ProtectCall)
        )


async def confirm_turbo(
    ctx: wire.GenericContext, message_text: str, chain_name: str
) -> None:

    from trezor.lvglui.scrs.template import Turbo

    screen = Turbo(
        message_text,
        chain_name,
        ctx.primary_color,
        ctx.icon_path,
    )
    print(ctx.icon_path)
    await raise_if_cancelled(
        interact(ctx, screen, "turbo", ButtonRequestType.ProtectCall)
    )


async def confirm_sol_create_ata(
    ctx: wire.GenericContext,
    fee_payer: str,
    funding_account: str,
    associated_token_account: str,
    wallet_address: str,
    token_mint: str,
):
    from trezor.lvglui.scrs.template import SolCreateAssociatedTokenAccount

    screen = SolCreateAssociatedTokenAccount(
        fee_payer,
        funding_account,
        associated_token_account,
        wallet_address,
        token_mint,
        primary_color=ctx.primary_color,
    )
    await raise_if_cancelled(
        interact(ctx, screen, "sol_create_ata", ButtonRequestType.ProtectCall)
    )


async def confirm_sol_token_transfer(
    ctx: wire.GenericContext,
    from_addr: str,
    to_addr: str,
    amount: str,
    source_owner: str,
    fee_payer: str,
    token_mint: str = None,
):
    from trezor.strings import strip_amount

    striped_amount, striped = strip_amount(amount)
    title = _(i18n_keys.TITLE__SEND_MULTILINE).format(striped_amount)
    if should_show_details(ctx, to_addr, title):
        from trezor.lvglui.scrs.template import SolTokenTransfer

        screen = SolTokenTransfer(
            title,
            from_addr,
            to_addr,
            amount,
            source_owner,
            fee_payer,
            primary_color=ctx.primary_color,
            icon_path=ctx.icon_path,
            token_mint=token_mint,
            striped=striped,
        )
        await raise_if_cancelled(
            interact(ctx, screen, "sol_token_transfer", ButtonRequestType.ProtectCall)
        )


async def confirm_sol_memo(
    ctx: wire.GenericContext, title: str, memo: str, signer: str
) -> None:
    from trezor.lvglui.scrs.template import Message

    screen = Message(
        title,
        signer,
        memo,
        ctx.primary_color,
        ctx.icon_path,
        False,
        item_addr_title=_(i18n_keys.LIST_KEY__SIGNER__COLON),
    )
    await raise_if_cancelled(
        interact(ctx, screen, "sol_memo", ButtonRequestType.ProtectCall)
    )


async def confirm_sol_message(
    ctx: wire.GenericContext,
    address: str,
    app_domain_fd: str | None,
    message: str,
    is_unsafe: bool = False,
) -> None:
    from trezor.lvglui.scrs.template import Message

    screen = Message(
        _(i18n_keys.TITLE__SIGN_STR_MESSAGE).format("SOL"),
        address,
        message,
        ctx.primary_color,
        ctx.icon_path,
        False,
        item_other=app_domain_fd,
        item_other_title="Application Domain:" if app_domain_fd else None,
        is_standard=not is_unsafe,
        warning_banner_text=_(i18n_keys.SECURITY__SOLANA_RAW_SIGNING_TX_WARNING)
        if is_unsafe
        else None,
    )
    await raise_if_cancelled(
        interact(ctx, screen, "confirm_sol_message", ButtonRequestType.ProtectCall)
    )


async def confirm_neo_token_transfer(
    ctx: wire.GenericContext,
    from_addr: str,
    to_addr: str,
    fee: str,
    amount: str,
    network_magic: int | None,
) -> None:
    from trezor.strings import strip_amount

    striped_amount, striped = strip_amount(amount)
    title = _(i18n_keys.TITLE__SEND_MULTILINE).format(striped_amount)
    from trezor.lvglui.scrs.template import NeoTokenTransfer

    screen = NeoTokenTransfer(
        title,
        from_addr=from_addr,
        to_addr=to_addr,
        fee=fee,
        amount=amount,
        primary_color=ctx.primary_color,
        icon_path=ctx.icon_path,
        striped=striped,
        network_magic=network_magic,
    )
    await raise_if_cancelled(
        interact(ctx, screen, "neo_token_transfer", ButtonRequestType.ProtectCall)
    )


async def confirm_neo_vote(
    ctx: wire.GenericContext,
    from_address: str,
    vote_to: str,
    is_remove_vote: bool,
    network_magic: int | None = None,
) -> None:
    from trezor.lvglui.scrs.template import NeoVote

    screen = NeoVote(
        from_address,
        vote_to,
        is_remove_vote,
        primary_color=ctx.primary_color,
        icon_path=ctx.icon_path,
        network_magic=network_magic,
    )
    await raise_if_cancelled(
        interact(ctx, screen, "neo_vote", ButtonRequestType.ProtectCall)
    )


async def confirm_final(
    ctx: wire.Context, chain_name: str, hold_level: int = 0
) -> None:
    from trezor.ui.layouts.lvgl import confirm_action

    await confirm_action(
        ctx,
        "confirm_final",
        title=_(i18n_keys.TITLE__CONFIRM_TRANSACTION),
        action=_(i18n_keys.SUBTITLE__DO_YOU_WANT_TO_SIGN__THIS_STR_TX).format(
            chain_name
        ),
        verb=_(i18n_keys.BUTTON__SLIDE_TO_SIGN),
        hold=True,
        anim_dir=0,
        icon=ctx.icon_path,
        hold_level=hold_level,
    )
    await show_popup(
        _(i18n_keys.TITLE__TRANSACTION_SIGNED),
        icon="A:/res/success.png",
        timeout_ms=2000,
    )


async def confirm_password_input(ctx: wire.Context) -> None:
    from trezor.ui.layouts.lvgl import confirm_action

    await confirm_action(
        ctx,
        "confirm_password_input",
        title=_(i18n_keys.MISTOUCH_PROTECTION_TITLE),
        action=_(i18n_keys.CONTENT__STR_FAILED_TRIES_SLIDE_TO_CONTINUE),
        verb=_(i18n_keys.MISTOUCH_PROTECTION_SLIDE_TEXT),
        verb_cancel=_(i18n_keys.BUTTON__BACK),
        hold=True,
        anim_dir=0,
        icon="A:/res/protection.png",
    )


async def confirm_blind_sign_common(
    ctx: wire.Context, signer: str, raw_message: bytes | bytearray
) -> None:

    from trezor.lvglui.scrs.template import BlindingSignCommon

    screen = BlindingSignCommon(signer, ctx.primary_color, ctx.icon_path)
    await raise_if_cancelled(
        interact(ctx, screen, "common_blinding_sign", ButtonRequestType.ProtectCall)
    )
    data_size = len(raw_message)
    await confirm_data(
        ctx,
        "confirm_data",
        title=_(i18n_keys.TITLE__VIEW_DATA),
        description=_(i18n_keys.SUBTITLE__STR_BYTES).format(data_size),
        data=raw_message,
        br_code=ButtonRequestType.SignTx,
    )


async def show_onekey_app_guide():
    if not __debug__:
        from trezor.lvglui.scrs import app_guide

        app_guide.GuideAppDownload()
        await app_guide.request()

        from apps.base import set_homescreen

        set_homescreen()


async def enable_airgap_mode() -> None:
    from trezor.lvglui.scrs.template import AirgapMode, AirGapToggleTips
    from trezor import utils

    scr_airgap = AirgapMode()
    reject = await scr_airgap.request()
    if not reject:
        scr_tips = AirGapToggleTips(enable=True)
        enable = await scr_tips.request()
        if enable:
            utils.enable_airgap_mode()


async def confirm_set_homescreen(ctx, replace: bool = False):
    await confirm_action(
        ctx=ctx,
        br_type="confirm_homescreen",
        title=_(i18n_keys.TITLE__SET_AS_HOMESCREEN),
        description=_(i18n_keys.SUBTITLE__SET_AS_HOMESCREEN)
        if not replace
        else _(i18n_keys.SUBTITLE__SET_HOMESCREEN_AND_DELETE),
        icon=None,
        anim_dir=2,
    )


async def confirm_collect_nft(ctx, replace: bool = False):
    await confirm_action(
        ctx=ctx,
        br_type="confirm_collect_nft",
        title=_(i18n_keys.TITLE__COLLECT_NFT),
        description=_(i18n_keys.SUBTITLE__COLLECT_NFT)
        if not replace
        else _(i18n_keys.SUBTITLE__COLLECT_NFT_AND_DELETE),
        icon=None,
        anim_dir=2,
    )


async def confirm_update_res(ctx, update_boot: bool = False):
    from trezor.lvglui.scrs.template import Modal

    confirm_screen = Modal(
        title=_(i18n_keys.TITLE__BOOTLOADER_UPDATE)
        if update_boot
        else _(i18n_keys.TITLE__RESOURCE_UPDATE),
        subtitle=_(i18n_keys.SUBTITLE__BOOTLOADER_UPDATE)
        if update_boot
        else _(i18n_keys.SUBTITLE__RESOURCE_UPDATE),
        confirm_text=_(i18n_keys.BUTTON__UPDATE),
        cancel_text=_(i18n_keys.BUTTON__CANCEL),
        anim_dir=2,
    )
    await raise_if_cancelled(interact(ctx, confirm_screen, "confirm_update_res"))


async def confirm_del_wallpaper(ctx, confirm_callback):
    from trezor.lvglui.scrs.common import FullSizeWindow

    confirm_screen = FullSizeWindow(
        title=_(i18n_keys.TITLE__DELETE_WALLPAPER),
        subtitle=_(i18n_keys.SUBTITLE__DELETE_WALLPAPER),
        confirm_text=_(i18n_keys.BUTTON__DELETE),
        cancel_text=_(i18n_keys.BUTTON__CANCEL),
    )
    confirm_screen.btn_yes.enable(
        bg_color=lv_colors.ONEKEY_RED_1, text_color=lv_colors.BLACK
    )
    confirm = await ctx.wait(confirm_screen.request())
    if confirm:
        confirm_callback()


async def confirm_remove_nft(ctx, confirm_callback, icon_path):
    from trezor.lvglui.scrs.template import NftRemoveConfirm

    confirm_screen = NftRemoveConfirm(icon_path)
    confirm = await ctx.wait(confirm_screen.request())
    if confirm:
        confirm_callback()


async def confirm_algo_payment(
    ctx: wire.GenericContext,
    sender: str,
    receiver: str,
    close_to: str | None = None,
    rekey_to: str | None = None,
    genesis_id: str | None = None,
    note: str | None = None,
    fee: str = 0,
    amount: str = 0,
) -> None:
    from trezor.lvglui.scrs.template import AlgoPayment
    from trezor.strings import strip_amount

    striped_amount, striped = strip_amount(amount)
    title = _(i18n_keys.TITLE__SEND_MULTILINE).format(striped_amount)
    if await should_show_details(ctx, receiver, title):
        screen = AlgoPayment(
            title,
            sender,
            receiver,
            close_to,
            rekey_to,
            genesis_id,
            note,
            fee,
            amount,
            ctx.primary_color,
            ctx.icon_path,
            striped=striped,
        )
        await raise_if_cancelled(
            interact(ctx, screen, "algo_payment", ButtonRequestType.ProtectCall)
        )


async def confirm_algo_asset_freeze(
    ctx: wire.GenericContext,
    sender: str | None = None,
    rekey_to: str | None = None,
    fee: str = 0,
    index: str = 0,
    target: str | None = None,
    new_freeze_state: bool = None,
    genesis_id: str | None = None,
    note: str | None = None,
) -> None:
    from trezor.lvglui.scrs.template import AlgoAssetFreeze, AlgoCommon

    screen = AlgoCommon("Asset Freeze", ctx.primary_color, ctx.icon_path)
    await raise_if_cancelled(
        interact(ctx, screen, "algo_asset_freeze", ButtonRequestType.ProtectCall)
    )
    screen = AlgoAssetFreeze(
        sender,
        rekey_to,
        fee,
        index,
        target,
        new_freeze_state,
        genesis_id,
        note,
        ctx.primary_color,
    )
    await raise_if_cancelled(
        interact(ctx, screen, "algo_asset_freeze", ButtonRequestType.ProtectCall)
    )


async def confirm_algo_asset_xfer(
    ctx: wire.GenericContext,
    sender: str,
    receiver: str,
    index: str = 0,
    fee: str = 0,
    amount: str = 0,
    close_assets_to: str | None = None,
    revocation_target: str | None = None,
    rekey_to: str | None = None,
    genesis_id: str | None = None,
    note: str | None = None,
) -> None:
    from trezor.lvglui.scrs.template import AlgoAssetXfer
    from trezor.strings import strip_amount

    striped_amount, striped = strip_amount(amount)
    title = _(i18n_keys.TITLE__SEND_MULTILINE).format(striped_amount)
    if await should_show_details(ctx, receiver, title):
        screen = AlgoAssetXfer(
            title,
            sender,
            receiver,
            index,
            fee,
            amount,
            close_assets_to,
            revocation_target,
            rekey_to,
            genesis_id,
            note,
            ctx.primary_color,
            ctx.icon_path,
            striped=striped,
        )
        await raise_if_cancelled(
            interact(ctx, screen, "algo_asset_transfer", ButtonRequestType.ProtectCall)
        )


async def confirm_algo_asset_cfg(
    ctx: wire.GenericContext,
    fee: str,
    sender: str,
    index: str | None = None,
    total: str | None = None,
    default_frozen: bool = None,
    unit_name: str | None = None,
    asset_name: str | None = None,
    decimals: str | None = None,
    manager: str | None = None,
    reserve: str | None = None,
    freeze: str | None = None,
    clawback: str | None = None,
    url: str | None = None,
    metadata_hash: str | None = None,
    rekey_to: str | None = None,
    genesis_id: str | None = None,
    note: str | None = None,
) -> None:
    from trezor.lvglui.scrs.template import AlgoAssetCfg, AlgoCommon

    screen = AlgoCommon("ASSET CONFIG", ctx.primary_color, ctx.icon_path)
    await raise_if_cancelled(
        interact(ctx, screen, "algo_asset_cfg", ButtonRequestType.ProtectCall)
    )
    screen = AlgoAssetCfg(
        fee,
        sender,
        index,
        total,
        default_frozen,
        unit_name,
        asset_name,
        decimals,
        manager,
        reserve,
        freeze,
        clawback,
        url,
        metadata_hash,
        rekey_to,
        genesis_id,
        note,
        ctx.primary_color,
    )
    await raise_if_cancelled(
        interact(ctx, screen, "algo_asset_cfg", ButtonRequestType.ProtectCall)
    )


async def confirm_algo_keyregNonparticipating(
    ctx: wire.GenericContext,
    sender: str,
    fee: str,
    nonpart: bool,
    rekey_to: str | None = None,
    genesis_id: str | None = None,
    note: str | None = None,
) -> None:
    from trezor.lvglui.scrs.template import AlgoKeyregNonp, AlgoCommon

    screen = AlgoCommon("KEYREG NO PARTICIPATING", ctx.primary_color, ctx.icon_path)
    await raise_if_cancelled(
        interact(ctx, screen, "algo_keyreg_Nonp", ButtonRequestType.ProtectCall)
    )
    screen = AlgoKeyregNonp(
        sender, fee, nonpart, rekey_to, genesis_id, note, ctx.primary_color
    )
    await raise_if_cancelled(
        interact(ctx, screen, "algo_keyreg_Nonp", ButtonRequestType.ProtectCall)
    )


async def confirm_algo_keyregOnline(
    ctx: wire.GenericContext,
    format: str,
    sender: str,
    fee: str,
    votekey: str | None = None,
    selkey: str | None = None,
    votefst: str | None = None,
    votelst: str | None = None,
    votekd: str | None = None,
    sprfkey: str | None = None,
    rekey_to: str | None = None,
    genesis_id: str | None = None,
    note: str | None = None,
) -> None:
    from trezor.lvglui.scrs.template import AlgoKeyregOnline, AlgoCommon

    screen = AlgoCommon(format, ctx.primary_color, ctx.icon_path)
    await raise_if_cancelled(
        interact(ctx, screen, "algo_keyreg_online", ButtonRequestType.ProtectCall)
    )
    screen = AlgoKeyregOnline(
        sender,
        fee,
        votekey,
        selkey,
        sprfkey,
        rekey_to,
        genesis_id,
        note,
        ctx.primary_color,
    )
    await raise_if_cancelled(
        interact(ctx, screen, "algo_keyreg_online", ButtonRequestType.ProtectCall)
    )


async def confirm_algo_app(ctx: wire.Context, signer: str, raw_message: bytes) -> None:

    from trezor.lvglui.scrs.template import AlgoApplication

    screen = AlgoApplication(signer, ctx.primary_color, ctx.icon_path)
    await raise_if_cancelled(
        interact(ctx, screen, "common_blinding_sign", ButtonRequestType.ProtectCall)
    )
    data_size = len(raw_message)
    await confirm_data(
        ctx,
        "confirm_data",
        title=_(i18n_keys.TITLE__VIEW_DATA),
        description=_(i18n_keys.SUBTITLE__STR_BYTES).format(data_size),
        data=raw_message,
        br_code=ButtonRequestType.SignTx,
    )


async def confirm_ripple_payment(
    ctx: wire.GenericContext,
    title,
    sender: str | None = None,
    receiver: str | None = None,
    amount: str = 0,
    fee: str = 0,
    total: str | None = None,
    tag: str | None = None,
    striped: bool = False,
) -> None:
    from trezor.lvglui.scrs.template import RipplePayment

    screen = RipplePayment(
        title,
        sender,
        receiver,
        amount,
        fee,
        total,
        tag,
        primary_color=ctx.primary_color,
        icon_path=ctx.icon_path,
        striped=striped,
    )
    await raise_if_cancelled(
        interact(ctx, screen, "ripple_payment", ButtonRequestType.ProtectCall)
    )


async def confirm_filecoin_payment(
    ctx: wire.GenericContext,
    title,
    sender: str | None = None,
    receiver: str | None = None,
    amount: str | None = None,
    gaslimit: str | None = None,
    gasfeecap: str | None = None,
    gaspremium: str | None = None,
    total_amount: str | None = None,
    striped: bool = False,
) -> None:
    from trezor.lvglui.scrs.template import FilecoinPayment

    screen = FilecoinPayment(
        title,
        sender,
        receiver,
        amount,
        gaslimit,
        gasfeecap,
        gaspremium,
        total_amount,
        primary_color=ctx.primary_color,
        icon_path=ctx.icon_path,
        striped=striped,
    )
    await raise_if_cancelled(
        interact(ctx, screen, "filecoin_payment", ButtonRequestType.ProtectCall)
    )


async def cosmos_require_show_more(
    ctx: wire.GenericContext,
    types: str | None,
    value: str | None,
    address: str | None,
    amount: str | None,
    chain_name: str | None = None,
    br_code: ButtonRequestType = ButtonRequestType.ConfirmOutput,
) -> bool:
    from trezor.lvglui.scrs.template import CosmosTransactionOverview
    from trezor.strings import strip_amount

    striped = False
    if types is None and value is None:
        assert amount is not None
        striped_amount, striped = strip_amount(amount)
        title = _(i18n_keys.TITLE__SEND_MULTILINE).format(striped_amount)
    else:
        title = _(i18n_keys.TITLE__SIGN_STR_TRANSACTION).format(chain_name or "Cosmos")
    res = await interact(
        ctx,
        CosmosTransactionOverview(
            title,
            types,
            value,
            amount if striped else None,
            address,
            primary_color=ctx.primary_color,
            icon_path=ctx.icon_path,
        ),
        "confirm_output",
        br_code,
    )
    if not res:
        from trezor import loop

        await loop.sleep(300)
        raise wire.ActionCancelled()
    elif res == 2:  # show more
        return True
    else:  # confirm
        return False


async def confirm_cosmos_send(
    ctx: wire.GenericContext,
    fee: str,
    chain_id: str,
    amount: str,
    chain_name: str | None,
    sender: str | None = None,
    receiver: str | None = None,
    memo: str | None = None,
) -> None:
    from trezor.lvglui.scrs.template import CosmosSend
    from trezor.strings import strip_amount

    striped_amount, striped = strip_amount(amount)

    screen = CosmosSend(
        _(i18n_keys.TITLE__SEND_MULTILINE).format(striped_amount),
        chain_id,
        chain_name,
        sender,
        receiver,
        amount,
        fee,
        memo,
        primary_color=ctx.primary_color,
        icon_path=ctx.icon_path,
        striped=striped,
    )
    await raise_if_cancelled(
        interact(ctx, screen, "cosmos_send", ButtonRequestType.ProtectCall)
    )


async def confirm_cosmos_delegate(
    ctx: wire.GenericContext,
    fee: str,
    chain_id: str,
    chain_name: str | None,
    delegator: str | None = None,
    validator: str | None = None,
    amount: str | None = None,
    memo: str | None = None,
) -> None:
    from trezor.lvglui.scrs.template import CosmosDelegate

    screen = CosmosDelegate(
        _(i18n_keys.TITLE__DELEGATE),
        chain_id,
        chain_name,
        delegator,
        validator,
        amount,
        fee,
        memo,
        primary_color=ctx.primary_color,
    )
    await raise_if_cancelled(
        interact(ctx, screen, "cosmos_delegate", ButtonRequestType.ProtectCall)
    )


async def confirm_cosmos_sign_common(
    ctx: wire.GenericContext,
    chain_id: str,
    chain_name: str | None,
    signer: str | None,
    fee: str,
    msgs_item: dict,
    title: str,
    value: str,
    memo: str | None = None,
) -> None:
    from trezor.lvglui.scrs.template import (
        CosmosSignCommon,
        CosmosSignContent,
        CosmosLongValue,
    )

    screen = CosmosSignCommon(
        chain_id, chain_name, signer, fee, title, value, memo, ctx.primary_color
    )
    await raise_if_cancelled(
        interact(ctx, screen, "cosmos_sign_common", ButtonRequestType.ProtectCall)
    )
    screen = CosmosSignContent(msgs_item, primary_color=ctx.primary_color)
    await raise_if_cancelled(
        interact(ctx, screen, "cosmos_sign_common", ButtonRequestType.ProtectCall)
    )

    for key, value in msgs_item.items():
        if len(str(value)) > 80:
            screen = CosmosLongValue(key, str(value), ctx.primary_color)
            await raise_if_cancelled(
                interact(
                    ctx, screen, "cosmos_sign_common", ButtonRequestType.ProtectCall
                )
            )


async def confirm_cosmos_memo(
    ctx: wire.GenericContext, title: str, description: str, memo: str
) -> None:
    from trezor.lvglui.scrs.template import BlobDisPlay

    screen = BlobDisPlay(
        title, description, memo, None, primary_color=ctx.primary_color
    )
    await raise_if_cancelled(
        interact(ctx, screen, "cosmos_memo", ButtonRequestType.ProtectCall)
    )


async def confirm_cosmos_sign_combined(
    ctx: wire.GenericContext,
    chain_id: str,
    signer: str | None,
    fee: str,
    msgs: str,
) -> None:
    from trezor.lvglui.scrs.template import CosmosSignCombined

    screen = CosmosSignCombined(chain_id, signer, fee, msgs, ctx.primary_color)
    await raise_if_cancelled(
        interact(
            ctx, screen, "confirm_cosmos_sign_combined", ButtonRequestType.ProtectCall
        )
    )


async def confirm_sign_typed_hash(
    ctx: wire.GenericContext, domain_hash: str, message_hash: str
) -> None:
    from trezor.lvglui.scrs.template import ConfirmTypedHash

    screen = ConfirmTypedHash(
        _(i18n_keys.TITLE__STR_TYPED_HASH).format(ctx.name),
        ctx.icon_path,
        domain_hash,
        message_hash,
        ctx.primary_color,
    )
    await raise_if_cancelled(
        interact(ctx, screen, "confirm_sign_typed_hash", ButtonRequestType.ProtectCall)
    )


async def backup_with_keytag(
    ctx: wire.GenericContext, mnemonics: bytes, recovery_check: bool = False
) -> None:
    from trezor.lvglui.scrs.common import FullSizeWindow

    while True:
        ask_screen = FullSizeWindow(
            _(i18n_keys.TITLE__BACK_UP_WITH_KEYTAG),
            _(i18n_keys.SUBTITLE__BACK_UP_WITH_KEYTAG),
            confirm_text=_(i18n_keys.BUTTON__BACKUP),
            cancel_text=_(i18n_keys.BUTTON__NOT_NOW),
            icon_path="A:/res/icon-dotmap.png",
            anim_dir=0,
        )
        ask_screen.btn_layout_ver()
        if await ctx.wait(ask_screen.request()):
            while True:
                from trezor.lvglui.scrs.bip39_dotmap import Bip39DotMap

                screen = Bip39DotMap(len(mnemonics.decode().split()))
                screen.show(mnemonics.decode())
                if await ctx.wait(screen.request()):
                    if recovery_check:
                        break
                    final_confirm = FullSizeWindow(
                        _(i18n_keys.TITLE__FINISH_KEYTAG_BACKUP),
                        _(i18n_keys.SUBTITLE__FINISH_KEYTAG_BACKUP),
                        confirm_text=_(i18n_keys.BUTTON__DONE),
                        cancel_text=_(i18n_keys.BUTTON__CANCEL),
                        icon_path="A:/res/icon-tips-blue.png",
                        anim_dir=0,
                    )
                    if await ctx.wait(final_confirm.request()):
                        break
            break
        else:
            break


async def confirm_polkadot_balances(
    ctx: wire.GenericContext,
    chain_name: str,
    module: str,
    method: str,
    sender: str,
    dest: str,
    balance: str,
    source: str | None = None,
    tip: str | None = None,
    keep_alive: str | None = None,
) -> None:
    from trezor.lvglui.scrs.template import PolkadotBalances
    from trezor.strings import strip_amount

    striped_amount, striped = strip_amount(balance)
    title = _(i18n_keys.TITLE__SEND_MULTILINE).format(striped_amount)
    if await should_show_details(ctx, dest, title):
        screen = PolkadotBalances(
            title,
            chain_name,
            module,
            method,
            sender,
            dest,
            source,
            balance,
            tip,
            keep_alive,
            ctx.primary_color,
            ctx.icon_path,
            striped=striped,
        )
        await raise_if_cancelled(
            interact(ctx, screen, "polkadot_balance", ButtonRequestType.ProtectCall)
        )


async def confirm_ton_transfer(
    ctx: wire.GenericContext,
    from_addr: str,
    to_addr: str,
    amount: str,
    memo: str | None,
):
    from trezor.lvglui.scrs.template import TonTransfer

    screen = TonTransfer(from_addr, to_addr, amount, memo, ctx.primary_color)

    await raise_if_cancelled(
        interact(ctx, screen, "confirm_ton_transfer", ButtonRequestType.ProtectCall)
    )


async def confirm_ton_connect(
    ctx: wire.GenericContext,
    domain: str,
    addr: str,
    payload: str | None,
):
    from trezor.lvglui.scrs.template import TonConnect

    screen = TonConnect(domain, addr, payload, ctx.primary_color)

    await raise_if_cancelled(
        interact(ctx, screen, "confirm_ton_connect", ButtonRequestType.ProtectCall)
    )


async def confirm_ton_signverify(
    ctx: wire.GenericContext,
    coin: str,
    message: str,
    address: str,
    domain: str,
    verify: bool,
) -> None:
    if verify:
        header = _(i18n_keys.TITLE__VERIFY_STR_MESSAGE).format(coin)
        br_type = "verify_message"
    else:
        header = _(i18n_keys.TITLE__SIGN_STR_MESSAGE).format(coin)
        br_type = "sign_message"
    from trezor.lvglui.scrs.template import TonMessage

    await raise_if_cancelled(
        interact(
            ctx,
            TonMessage(
                header,
                address,
                message,
                domain,
                ctx.primary_color,
                ctx.icon_path,
                verify,
            ),
            br_type,
            ButtonRequestType.Other,
        )
    )


def confirm_unknown_token_transfer(
    ctx: wire.GenericContext,
    address: str,
):
    return confirm_address(
        ctx,
        _(i18n_keys.TITLE__UNKNOWN_TOKEN),
        address,
        description=_(i18n_keys.LIST_KEY__CONTRACT_ADDRESS__COLON),
        br_type="unknown_token",
        icon="A:/res/warning.png",
        icon_color=ui.ORANGE,
        br_code=ButtonRequestType.SignTx,
    )


async def confirm_tron_freeze(
    ctx: wire.GenericContext,
    title: str,
    sender: str,
    resource: str | None = None,
    balance: str | None = None,
    duration: str | None = None,
    receiver: str | None = None,
) -> None:
    from trezor.lvglui.scrs.template import TronAssetFreeze, AlgoCommon

    screen = AlgoCommon(title, ctx.primary_color, ctx.icon_path)
    await raise_if_cancelled(
        interact(ctx, screen, "tron_asset_freeze", ButtonRequestType.ProtectCall)
    )
    screen = TronAssetFreeze(
        True,
        sender,
        resource,
        balance,
        duration,
        receiver,
        None,
        ctx.primary_color,
    )
    await raise_if_cancelled(
        interact(ctx, screen, "tron_asset_freeze", ButtonRequestType.ProtectCall)
    )


async def confirm_tron_unfreeze(
    ctx: wire.GenericContext,
    title: str,
    sender: str,
    resource: str | None = None,
    balance: str | None = None,
) -> None:
    from trezor.lvglui.scrs.template import TronAssetFreeze, AlgoCommon

    screen = AlgoCommon(title, ctx.primary_color, ctx.icon_path)
    await raise_if_cancelled(
        interact(ctx, screen, "tron_asset_freeze_v2", ButtonRequestType.ProtectCall)
    )
    screen = TronAssetFreeze(
        False,
        sender,
        resource,
        balance,
        None,
        None,
        None,
        ctx.primary_color,
    )
    await raise_if_cancelled(
        interact(ctx, screen, "tron_asset_freeze_v2", ButtonRequestType.ProtectCall)
    )


async def confirm_tron_delegate(
    ctx: wire.GenericContext,
    title: str,
    sender: str,
    resource: str | None = None,
    balance: str | None = None,
    receiver: str | None = None,
    lock: str | None = None,
) -> None:
    from trezor.lvglui.scrs.template import TronAssetFreeze, AlgoCommon

    screen = AlgoCommon(title, ctx.primary_color, ctx.icon_path)
    await raise_if_cancelled(
        interact(ctx, screen, "confirm_tron_delegate", ButtonRequestType.ProtectCall)
    )
    screen = TronAssetFreeze(
        False,
        sender,
        resource,
        balance,
        None,
        receiver,
        lock,
        ctx.primary_color,
    )
    await raise_if_cancelled(
        interact(ctx, screen, "confirm_tron_delegate", ButtonRequestType.ProtectCall)
    )


async def confirm_tron_vote(
    ctx: wire.GenericContext,
    title: str,
    voter: str,
    votes: list[tuple[str, int]],
) -> None:
    from trezor.lvglui.scrs.template import TronVoteWitness, AlgoCommon

    screen = AlgoCommon(title, ctx.primary_color, ctx.icon_path)
    await raise_if_cancelled(
        interact(
            ctx, screen, "confirm_tron_vote_overview", ButtonRequestType.ProtectCall
        )
    )
    screen = TronVoteWitness(voter, votes, ctx.primary_color)
    await raise_if_cancelled(
        interact(ctx, screen, "confirm_tron_vote", ButtonRequestType.ProtectCall)
    )


async def confirm_tron_common(
    ctx: wire.GenericContext,
    title: str,
) -> None:
    from trezor.lvglui.scrs.template import AlgoCommon

    screen = AlgoCommon(title, ctx.primary_color, ctx.icon_path)
    await raise_if_cancelled(
        interact(ctx, screen, "confirm_tron_common", ButtonRequestType.ProtectCall)
    )


async def show_ur_response(
    ctx: wire.GenericContext,
    title: str | None,
    qr_code: str | None,
    encoder=None,
) -> None:
    from trezor.lvglui.scrs.template import UrResponse

    screen = UrResponse(
        title,
        _(i18n_keys.TITLE_CONFIRM_ADDRESS_DESC),
        qr_code=qr_code,
        encoder=encoder,
    )
    await ctx.wait(screen.request())


async def confirm_nostrmessage(
    ctx: wire.GenericContext,
    address: str,
    message: str,
    encrypt: bool,
    title: str,
) -> None:
    from trezor.lvglui.scrs.template import Message

    if encrypt:
        br_type = "verify_message"
    else:
        br_type = "sign_message"
    await raise_if_cancelled(
        interact(
            ctx,
            Message(
                title,
                address,
                message,
                ctx.primary_color,
                ctx.icon_path,
                encrypt,
            ),
            br_type,
            ButtonRequestType.Other,
        )
    )


async def confirm_lnurl_auth(
    ctx: wire.GenericContext,
    title: str,
    domain: str,
    data: str,
) -> None:
    from trezor.lvglui.scrs.template import Message

    br_type = "sign_message"
    await raise_if_cancelled(
        interact(
            ctx,
            Message(
                title,
                domain,
                data,
                ctx.primary_color,
                ctx.icon_path,
                True,
                item_addr_title=_(i18n_keys.LIST_KEY__DOMAIN__COLON),
            ),
            br_type,
            ButtonRequestType.Other,
        )
    )


async def confirm_near_transfer(
    ctx: wire.GenericContext,
    sender: str,
    receiver: str,
    amount: str,
) -> None:
    from trezor.lvglui.scrs.template import TransactionDetailsNear
    from trezor.strings import strip_amount

    striped_amount, striped = strip_amount(amount)
    title = _(i18n_keys.TITLE__SEND_MULTILINE).format(striped_amount)
    if await should_show_details(ctx, receiver, title):
        screen = TransactionDetailsNear(
            title,
            sender,
            receiver,
            amount,
            ctx.primary_color,
            ctx.icon_path,
            striped=striped,
        )
        await raise_if_cancelled(
            interact(ctx, screen, "near_transfer", ButtonRequestType.ProtectCall)
        )


async def confirm_safe_tx(
    ctx: wire.GenericContext,
    from_address: str,
    to_addr: str,
    value: str,
    call_data: bytes | None,
    operation: int,
    safe_tx_gas: int,
    base_gas: int,
    gas_price: str,
    gas_token: str,
    refund_receiver: str,
    nonce: int,
    verifying_contract: str,
    domain_hash: str,
    message_hash: str,
    safe_tx_hash: str,
) -> None:
    from trezor.lvglui.scrs.template import GnosisSafeTxDetails

    screen = GnosisSafeTxDetails(
        from_address,
        to_addr,
        value,
        call_data,
        operation,
        safe_tx_gas,
        base_gas,
        gas_price,
        gas_token,
        refund_receiver,
        nonce,
        verifying_contract,
        ctx.icon_path,
        ctx.primary_color,
        domain_hash,
        message_hash,
        safe_tx_hash,
    )
    await raise_if_cancelled(
        interact(ctx, screen, "confirm_safe_tx", ButtonRequestType.ProtectCall)
    )


async def confirm_safe_approve_hash(
    ctx: wire.GenericContext,
    title: str,
    from_address: str,
    to_address: str,
    hash_to_approve: str,
    nonce: str,
    fee_max: str,
    is_eip1559: bool,
    gas_price: str | None = None,
    max_priority_fee_per_gas: str | None = None,
    max_fee_per_gas: str | None = None,
    chain_id: int | None = None,
) -> None:
    from trezor.lvglui.scrs.template import SafeTxSafeApproveHash

    screen = SafeTxSafeApproveHash(
        title,
        from_address,
        to_address,
        hash_to_approve,
        nonce,
        fee_max,
        is_eip1559,
        gas_price,
        max_priority_fee_per_gas,
        max_fee_per_gas,
        ctx.primary_color,
        ctx.icon_path,
        chain_id=chain_id,
    )
    await raise_if_cancelled(
        interact(
            ctx, screen, "confirm_safe_approve_hash", ButtonRequestType.ProtectCall
        )
    )


async def confirm_safe_exec_transaction(
    ctx: wire.GenericContext,
    from_address: str,
    to_address: str,
    to_address_safe: str,
    value_safe: str,
    operation: int,
    safe_tx_gas: str,
    base_gas: str,
    gas_price_safe: str,
    gas_token: str,
    refund_receiver: str,
    signatures: str,
    fee_max: str,
    nonce: int,
    is_eip1559: bool = True,
    chain_id: int | None = None,
    call_data: str | dict[str, str] | None = None,
    call_method: str | None = None,
    gas_price: str | None = None,
    max_priority_fee_per_gas: str | None = None,
    max_fee_per_gas: str | None = None,
) -> None:
    from trezor.lvglui.scrs.template import SafeTxExecTransaction

    screen = SafeTxExecTransaction(
        from_address=from_address,
        to_address=to_address,
        to_address_safe=to_address_safe,
        value_safe=value_safe,
        operation=operation,
        safe_tx_gas=safe_tx_gas,
        base_gas=base_gas,
        gas_price_safe=gas_price_safe,
        gas_token=gas_token,
        refund_receiver=refund_receiver,
        signatures=signatures,
        fee_max=fee_max,
        nonce=nonce,
        chain_id=chain_id,
        is_eip1559=is_eip1559,
        call_data=call_data,
        call_method=call_method,
        gas_price=gas_price,
        max_priority_fee_per_gas=max_priority_fee_per_gas,
        max_fee_per_gas=max_fee_per_gas,
        icon_path=ctx.icon_path,
        primary_color=ctx.primary_color,
    )
    await raise_if_cancelled(
        interact(
            ctx, screen, "confirm_safe_exec_transaction", ButtonRequestType.ProtectCall
        )
    )
