from typing import TYPE_CHECKING

from storage.device import is_initialized
from trezor import config, wire
from trezor.lvglui.i18n import gettext as _, keys as i18n_keys
from trezor.lvglui.lv_colors import lv_colors
from trezor.messages import Success
from trezor.ui.layouts import confirm_action, show_success

from apps.common.request_pin import (
    error_pin_invalid,
    error_pin_matches_wipe_code,
    error_pin_used,
    request_pin_and_sd_salt,
    request_pin_confirm,
)

if TYPE_CHECKING:
    from typing import Awaitable

    from trezor.messages import ChangePin


async def change_pin(ctx: wire.Context, msg: ChangePin) -> Success:
    if not is_initialized():
        raise wire.NotInitialized("Device is not initialized")
    # confirm that user wants to change the pin
    await require_confirm_change_pin(ctx, msg)
    # get old pin
    curpin, salt = await request_pin_and_sd_salt(
        ctx,
        _(i18n_keys.TITLE__ENTER_OLD_PIN),
        allow_fingerprint=False,
        standy_wall_only=True,
    )
    # if changing pin, pre-check the entered pin before getting new pin
    from apps.common.pin_constants import PinType, PinResult

    if curpin and not msg.remove:
        result = config.check_pin(curpin, salt, PinType.USER_CHECK)
        if isinstance(result, tuple):
            verified, usertype = result
        else:
            verified = result
            usertype = PinType.USER_CHECK
        if not verified:
            await error_pin_invalid(ctx)

    # get new pin
    if not msg.remove:
        newpin = await request_pin_confirm(
            ctx, show_tip=(not bool(curpin)), allow_fingerprint=False
        )
    else:
        newpin = ""

    if newpin:
        result = config.check_pin(newpin, salt, PinType.PASSPHRASE_PIN)
        if isinstance(result, tuple):
            verified, usertype = result
        else:
            verified = result
            usertype = PinResult.PASSPHRASE_PIN_ENTERED
        if usertype == PinResult.PASSPHRASE_PIN_ENTERED:
            return await error_pin_used(ctx)

    # write into storage
    if not config.change_pin(curpin, newpin, salt, salt):
        if newpin:
            await error_pin_matches_wipe_code(ctx)
        else:
            await error_pin_invalid(ctx)

    if newpin:
        if curpin:
            msg_screen = _(i18n_keys.SUBTITLE__SET_PIN_PIN_CHANGED)
            msg_wire = _(i18n_keys.TITLE__PIN_CHANGED)
        else:
            msg_screen = _(i18n_keys.SUBTITLE__SETUP_SET_PIN_PIN_ENABLED)
            msg_wire = _(i18n_keys.TITLE__PIN_ENABLED)
    else:
        msg_screen = _(i18n_keys.SUBTITLE__SET_PIN_PIN_DISABLED)
        msg_wire = _(i18n_keys.TITLE__PIN_DISABLED)

    await show_success(
        ctx,
        "success_pin",
        msg_screen,
        header=msg_wire,
        button=_(i18n_keys.BUTTON__DONE),
    )
    return Success(message=msg_wire)


def require_confirm_change_pin(ctx: wire.Context, msg: ChangePin) -> Awaitable[None]:
    has_pin = config.has_pin()

    if msg.remove and has_pin:  # removing pin
        return confirm_action(
            ctx,
            "set_pin",
            _(i18n_keys.TITLE__DISABLE_PIN_PROTECTION),
            description=_(i18n_keys.SUBTITLE__DISABLE_PIN_PROTECTION),
            action="",
            anim_dir=2,
            verb=_(i18n_keys.BUTTON__REMOVE),
            primary_color=lv_colors.ONEKEY_YELLOW,
        )

    if not msg.remove:  # changing pin

        return confirm_action(
            ctx,
            "set_pin",
            _(i18n_keys.TITLE__CHANGE_PIN),
            description=_(i18n_keys.SUBTITLE__SETUP_CREATE_ENABLE_PIN_PROTECTION),
            action="",
            anim_dir=2,
            primary_color=lv_colors.ONEKEY_YELLOW,
        )
    # if not msg.remove and has_pin:  # changing pin
    #     return confirm_action(
    #         ctx,
    #         "set_pin",
    #         _(i18n_keys.TITLE__CHANGE_PIN),
    #         description=_(i18n_keys.SUBTITLE__SET_PIN_CHANGE_PIN),
    #         action="",
    #         reverse=True,
    #         anim_dir=2,
    #     )

    # if not msg.remove and not has_pin:  # setting new pin
    #     return confirm_action(
    #         ctx,
    #         "set_pin",
    #         _(i18n_keys.TITLE__ENABLED_PIN),
    #         description=_(i18n_keys.SUBTITLE__SET_PIN_ENABLE_PIN),
    #         action="",
    #         reverse=True,
    #         anim_dir=2,
    #     )

    # removing non-existing PIN
    raise wire.ProcessError("PIN protection already disabled")
