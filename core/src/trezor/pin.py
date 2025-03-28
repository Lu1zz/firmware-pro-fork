from typing import Any

_previous_progress: int | None = None
_previous_seconds: int | None = None
keepalive_callback: Any = None


def show_pin_timeout(seconds: int, progress: int, message: str) -> bool:
    from trezor import ui

    global _previous_progress
    global _previous_seconds

    if callable(keepalive_callback):
        keepalive_callback()

    if progress == 0:
        if progress != _previous_progress:
            # avoid overdraw in case of repeated progress calls
            ui.display.clear()
            _previous_seconds = None
        # ui.display.text_center(ui.WIDTH // 2, 37, message, ui.BOLD, ui.FG, ui.BG)

    # if not utils.DISABLE_ANIMATION:
    else:
        ui.display.loader(progress, False, 0, ui.FG, ui.BG)

    if seconds != _previous_seconds:
        if seconds == 0:
            # remaining = ""
            ui.display.clear()
        # elif seconds == 1:
        #     remaining = "1 second left"
        # else:
        #     remaining = f"{seconds} seconds left"
        ui.display.bar(0, ui.HEIGHT - 42, ui.WIDTH, 25, ui.BG)
        # ui.display.text_center(
        #     ui.WIDTH // 2, ui.HEIGHT - 22, remaining, ui.BOLD, ui.FG, ui.BG
        # )
        _previous_seconds = seconds

    if progress == 1000:
        ui.display.clear()

    ui.refresh()
    _previous_progress = progress
    return False
