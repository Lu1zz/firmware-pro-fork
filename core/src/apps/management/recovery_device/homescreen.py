import storage
import storage.device
import storage.recovery
import storage.recovery_shares
from trezor import strings, utils, wire, workflow
from trezor.crypto import slip39
from trezor.crypto.hashlib import sha256
from trezor.enums import BackupType, MessageType
from trezor.errors import MnemonicError
from trezor.lvglui.i18n import gettext as _, keys as i18n_keys
from trezor.messages import Success
from trezor.ui.layouts import (
    enable_airgap_mode,
    show_onekey_app_guide,
    show_popup,
    show_success,
)

from apps.base import set_homescreen
from apps.common import mnemonic
from apps.homescreen.homescreen import homescreen

from .. import backup_types
from . import layout, recover


async def recovery_homescreen() -> None:
    if not storage.recovery.is_in_progress():
        workflow.set_default(homescreen)
        return

    # recovery process does not communicate on the wire
    ctx = wire.DUMMY_CONTEXT
    await recovery_process(ctx)


async def recovery_process(ctx: wire.GenericContext) -> Success:
    wire.AVOID_RESTARTING_FOR = (MessageType.Initialize, MessageType.GetFeatures)
    try:
        return await _continue_recovery_process(ctx)
    except recover.RecoveryAborted:
        dry_run = storage.recovery.is_dry_run()
        if dry_run:
            storage.recovery.end_progress()
        else:
            await show_popup(_(i18n_keys.TITLE__PLEASE_WAIT))
            storage.wipe()
        raise wire.ActionCancelled


async def _continue_recovery_process(ctx: wire.GenericContext) -> Success:
    # gather the current recovery state from storage
    dry_run = storage.recovery.is_dry_run()
    word_count, backup_type = recover.load_slip39_state()

    # Both word_count and backup_type are derived from the same data. Both will be
    # either set or unset. We use 'backup_type is None' to detect status of both.
    # The following variable indicates that we are (re)starting the first recovery step,
    # which includes word count selection.
    is_first_step = backup_type is None

    if not is_first_step:
        assert word_count is not None
        # If we continue recovery, show starting screen with word count immediately.
        await _request_share_first_screen(ctx, word_count)

    secret = None
    while secret is None:
        if is_first_step:
            # If we are starting recovery, ask for word count first...
            if not word_count:
                word_count = await _request_word_count(ctx, dry_run)
            # ...and only then show the starting screen with word count.
            await _request_share_first_screen(ctx, word_count)
        assert word_count is not None

        # ask for mnemonic words one by one
        try:
            words = await layout.request_mnemonic(ctx, word_count, backup_type)
        except wire.ActionCancelled:
            continue

        # if they were invalid or some checks failed we continue and request them again
        if not words:
            continue

        try:
            await show_popup(_(i18n_keys.TITLE__PLEASE_WAIT))
            secret, backup_type = await _process_words(ctx, words)
            # If _process_words succeeded, we now have both backup_type (from
            # its result) and word_count (from _request_word_count earlier), which means
            # that the first step is complete.
            is_first_step = False
        except MnemonicError:
            await layout.show_invalid_mnemonic(ctx, word_count)

    assert backup_type is not None
    if dry_run:
        result = await _finish_recovery_dry_run(ctx, secret, backup_type)
    else:
        result = await _finish_recovery(ctx, secret, backup_type)

    return result


async def _finish_recovery_dry_run(
    ctx: wire.GenericContext, secret: bytes, backup_type: BackupType
) -> Success:
    if backup_type is None:
        raise RuntimeError

    if utils.USE_THD89:
        is_slip39 = backup_types.is_slip39_backup_type(backup_type)
        if is_slip39:
            raise wire.ProcessError("THD89 does not support SLIP-39")

        from trezor.crypto import se_thd89

        result = se_thd89.check(secret)

    else:
        digest_input = sha256(secret).digest()
        stored = mnemonic.get_secret()
        digest_stored = sha256(stored).digest()
        result = utils.consteq(digest_stored, digest_input)

        is_slip39 = backup_types.is_slip39_backup_type(backup_type)
        # Check that the identifier and iteration exponent match as well
        if is_slip39:
            result &= (
                storage.device.get_slip39_identifier()
                == storage.recovery.get_slip39_identifier()
            )
            result &= (
                storage.device.get_slip39_iteration_exponent()
                == storage.recovery.get_slip39_iteration_exponent()
            )

    storage.recovery.end_progress()

    await layout.show_dry_run_result(ctx, result, is_slip39, secret)

    if result:
        return Success(message="The seed is valid and matches the one in the device")
    else:
        raise wire.ProcessError("The seed does not match the one in the device")


async def _finish_recovery(
    ctx: wire.GenericContext, secret: bytes, backup_type: BackupType
) -> Success:
    if backup_type is None:
        raise RuntimeError
    storage.device.store_mnemonic_secret(
        secret, backup_type, needs_backup=False, no_backup=False
    )
    if backup_type in (BackupType.Slip39_Basic, BackupType.Slip39_Advanced):
        identifier = storage.recovery.get_slip39_identifier()
        exponent = storage.recovery.get_slip39_iteration_exponent()
        if identifier is None or exponent is None:
            # Identifier and exponent need to be stored in storage at this point
            raise RuntimeError
        storage.device.set_slip39_identifier(identifier)
        storage.device.set_slip39_iteration_exponent(exponent)

    storage.recovery.end_progress()

    await show_success(
        ctx,
        "success_recovery",
        _(i18n_keys.SUBTITLE__DEVICE_RECOVER_WALLET_IS_READY),
        header=_(i18n_keys.TITLE__WALLET_IS_READY),
        button=_(i18n_keys.BUTTON__CONTINUE),
    )
    # ask user to open air-gapped mode
    await enable_airgap_mode()

    if isinstance(ctx, wire.DummyContext):
        utils.make_show_app_guide()
    else:
        await show_onekey_app_guide()
        set_homescreen()
    return Success(message="Device recovered")


async def _request_word_count(ctx: wire.GenericContext, dry_run: bool) -> int:
    # await layout.homescreen_dialog(
    #     ctx, _(i18n_keys.BUTTON__CONTINUE), _(i18n_keys.TITLE__SELECT_NUMBER_OF_WORDS)
    # )

    # ask for the number of words
    return await layout.request_word_count(ctx, dry_run)


async def _process_words(
    ctx: wire.GenericContext, words: str
) -> tuple[bytes | None, BackupType]:
    word_count = len(words.split(" "))
    is_slip39 = backup_types.is_slip39_word_count(word_count)

    share = None
    if not is_slip39:  # BIP-39
        secret: bytes | None = recover.process_bip39(words)
    else:
        secret, share = recover.process_slip39(words)

    backup_type = backup_types.infer_backup_type(is_slip39, share)
    if secret is None:  # SLIP-39
        assert share is not None
        if share.group_count and share.group_count > 1:
            await layout.show_group_share_success(ctx, share.index, share.group_index)
        await _request_share_next_screen(ctx)

    return secret, backup_type


async def _request_share_first_screen(
    ctx: wire.GenericContext, word_count: int
) -> None:
    if backup_types.is_slip39_word_count(word_count):
        remaining = storage.recovery.fetch_slip39_remaining_shares()
        if remaining:
            await _request_share_next_screen(ctx)
        else:
            await layout.homescreen_dialog(
                ctx, "Enter share", "Enter any share", f"({word_count} words)"
            )
    else:  # BIP-39
        btn_text = _(i18n_keys.BUTTON__CONTINUE)
        title = _(i18n_keys.TITLE__ENTER_RECOVERY_PHRASE)
        await layout.homescreen_dialog(ctx, btn_text, title, f"({word_count} words)")


async def _request_share_next_screen(ctx: wire.GenericContext) -> None:
    remaining = storage.recovery.fetch_slip39_remaining_shares()
    group_count = storage.recovery.get_slip39_group_count()
    if not remaining:
        # 'remaining' should be stored at this point
        raise RuntimeError

    if group_count > 1:
        await layout.homescreen_dialog(
            ctx,
            "Enter",
            "More shares needed",
            info_func=_show_remaining_groups_and_shares,
        )
    else:
        text = strings.format_plural("{count} more {plural}", remaining[0], "share")
        await layout.homescreen_dialog(ctx, "Enter share", text, "needed to enter")


async def _show_remaining_groups_and_shares(ctx: wire.GenericContext) -> None:
    """
    Show info dialog for Slip39 Advanced - what shares are to be entered.
    """
    shares_remaining = storage.recovery.fetch_slip39_remaining_shares()
    # should be stored at this point
    assert shares_remaining

    groups = set()
    first_entered_index = -1
    for i, group_count in enumerate(shares_remaining):
        if group_count < slip39.MAX_SHARE_COUNT:
            first_entered_index = i

    share = None
    for index, remaining in enumerate(shares_remaining):
        if 0 <= remaining < slip39.MAX_SHARE_COUNT:
            m = storage.recovery_shares.fetch_group(index)[0]
            if not share:
                share = slip39.decode_mnemonic(m)
            identifier = m.split(" ")[0:3]
            groups.add((remaining, tuple(identifier)))
        elif remaining == slip39.MAX_SHARE_COUNT:  # no shares yet
            identifier = storage.recovery_shares.fetch_group(first_entered_index)[
                0
            ].split(" ")[0:2]
            groups.add((remaining, tuple(identifier)))

    assert share  # share needs to be set
    return await layout.show_remaining_shares(
        ctx, groups, shares_remaining, share.group_threshold
    )
