from typing import *


# extmod/modtrezorconfig/modtrezorconfig.c
def init(
   ui_wait_callback: Callable[[int, int, str], bool] | None = None
) -> None:
    """
    Initializes the storage.  Must be called before any other method is
    called from this module!
    """


# extmod/modtrezorconfig/modtrezorconfig.c
def is_initialized() -> bool:
    """
    Returns True if device is initialized.
    """


# extmod/modtrezorconfig/modtrezorconfig.c
def unlock(pin: str, ext_salt: bytes | None, pin_use_type: int = 0)
-> tuple[bool, int]:
    """
    Attempts to unlock the storage with the given PIN and external salt.
    Returns True on success, False on failure.
    """


# extmod/modtrezorconfig/modtrezorconfig.c
def check_pin(pin: str, ext_salt: bytes | None, pin_use_type: int = 0) ->
bool:
    """
    Check the given PIN with the given external salt.
    Returns True on success, False on failure.
    """


# extmod/modtrezorconfig/modtrezorconfig.c
def lock() -> None:
    """
    Locks the storage.
    """


# extmod/modtrezorconfig/modtrezorconfig.c
def is_unlocked() -> bool:
    """
    Returns True if storage is unlocked, False otherwise.
    """


# extmod/modtrezorconfig/modtrezorconfig.c
def has_pin() -> bool:
    """
    Returns True if storage has a configured PIN, False otherwise.
    """


# extmod/modtrezorconfig/modtrezorconfig.c
def get_pin_rem() -> int:
    """
    Returns the number of remaining PIN entry attempts.
    """


# extmod/modtrezorconfig/modtrezorconfig.c
def change_pin(
    oldpin: str,
    newpin: str,
    old_ext_salt: bytes | None,
    new_ext_salt: bytes | None,
) -> bool:
    """
    Change PIN and external salt. Returns True on success, False on failure.
    """


# extmod/modtrezorconfig/modtrezorconfig.c
def ensure_not_wipe_code(pin: str) -> None:
    """
    Wipes the device if the entered PIN is the wipe code.
    """


# extmod/modtrezorconfig/modtrezorconfig.c
def has_wipe_code() -> bool:
    """
    Returns True if storage has a configured wipe code, False otherwise.
    """


# extmod/modtrezorconfig/modtrezorconfig.c
def change_wipe_code(
    pin: str,
    ext_salt: bytes | None,
    wipe_code: str,
) -> bool:
    """
    Change wipe code. Returns True on success, False on failure.
    """


# extmod/modtrezorconfig/modtrezorconfig.c
def get_needs_backup() -> bool:
    """
    Returns needs_backup.
    """


# extmod/modtrezorconfig/modtrezorconfig.c
def set_needs_backup(needs_backup: bool = False) -> bool:
    """
    Set needs_backup.
    """


# extmod/modtrezorconfig/modtrezorconfig.c
def get_val_len(app: int, key: int, public: bool = False) -> int:
    """
    Gets the length of the value of the given key for the given app (or None
    if not set). Raises a RuntimeError if decryption or authentication of
    the stored value fails.
    """


# extmod/modtrezorconfig/modtrezorconfig.c
def get(app: int, key: int, public: bool = False) -> bytes | None:
    """
    Gets the value of the given key for the given app (or None if not set).
    Raises a RuntimeError if decryption or authentication of the stored
    value fails.
    """


# extmod/modtrezorconfig/modtrezorconfig.c
def set(app: int, key: int, value: bytes, public: bool = False) -> None:
    """
    Sets a value of given key for given app.
    """


# extmod/modtrezorconfig/modtrezorconfig.c
def delete(
    app: int, key: int, public: bool = False, writable_locked: bool = False
) -> bool:
    """
    Deletes the given key of the given app.
    """


# extmod/modtrezorconfig/modtrezorconfig.c
def set_counter(
    app: int, key: int, count: int, writable_locked: bool = False
) -> None:
    """
    Sets the given key of the given app as a counter with the given value.
    """


# extmod/modtrezorconfig/modtrezorconfig.c
def next_counter(
   app: int, key: int, writable_locked: bool = False,
) -> int:
    """
    Increments the counter stored under the given key of the given app and
    returns the new value.
    """


# extmod/modtrezorconfig/modtrezorconfig.c
def wipe() -> None:
    """
    Erases the whole config. Use with caution!
    """


# extmod/modtrezorconfig/modtrezorconfig.c
def se_import_mnemonic(mnemonic: bytes) -> bool:
    """
    Import mnemonic to SE.
    """


# extmod/modtrezorconfig/modtrezorconfig.c
def se_import_slip39(mnemonic: bytes, backup_type: int, identifier: int |
None, iteration_exponent: int | None) -> bool:
    """
    Import slip39 to SE.
    """


# extmod/modtrezorconfig/modtrezorconfig.c
def se_export_mnemonic() -> bytes:
    """
    Export mnemonic from SE.
    """


# extmod/modtrezorconfig/modtrezorconfig.c
def fingerprint_is_unlocked() -> bool:
    """
    Returns True if fingerprint is unlocked, False otherwise.
    """


# extmod/modtrezorconfig/modtrezorconfig.c
def fingerprint_lock() -> bool:
    """
    fingerprint lock.
    """


# extmod/modtrezorconfig/modtrezorconfig.c
def fingerprint_unlock() -> bool:
    """
    fingerprint unlock.
    """


# extmod/modtrezorconfig/modtrezorconfig.c
def fingerprint_data_read() -> None:
    """
    fingerprint data read.
    """


# extmod/modtrezorconfig/modtrezorconfig.c
def fingerprint_data_inited() -> bool:
    """
    Returns True if fingerprint data is inited, False otherwise.
    """


# extmod/modtrezorconfig/modtrezorconfig.c
def fingerprint_data_read_remaining() -> None:
    """
    fingerprint data read remaining.
    """


# extmod/modtrezorconfig/modtrezorconfig.c
def get_serial() -> str:
    """
    get device serial
    """


# extmod/modtrezorconfig/modtrezorconfig.c
def get_capacity() -> str:
    """
    get emmc capacity
    """
