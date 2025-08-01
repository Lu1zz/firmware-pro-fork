from typing import TYPE_CHECKING

import storage.cache as cache
import storage.device as device
from trezor import utils, wire
from trezor.crypto import bip32, hmac

from . import mnemonic
from .passphrase import get as get_passphrase

if TYPE_CHECKING:
    from .paths import Bip32Path, Slip21Path


class Slip21Node:
    """
    This class implements the SLIP-0021 hierarchical derivation of symmetric keys, see
    https://github.com/satoshilabs/slips/blob/master/slip-0021.md.
    """

    def __init__(self, seed: bytes | None = None, data: bytes | None = None) -> None:
        if utils.USE_THD89:
            if data is not None:
                self.data = data
            else:
                from trezor.crypto import se_thd89

                self.data = se_thd89.slip21_node()
        else:
            assert seed is None or data is None, "Specify exactly one of: seed, data"
            if data is not None:
                self.data = data
            elif seed is not None:
                self.data = hmac(hmac.SHA512, b"Symmetric key seed", seed).digest()
            else:
                raise ValueError  # neither seed nor data specified

    def __del__(self) -> None:
        del self.data

    def derive_path(self, path: Slip21Path) -> None:
        for label in path:
            h = hmac(hmac.SHA512, self.data[0:32], b"\x00")
            h.update(label)
            self.data = h.digest()

    def key(self) -> bytes:
        return self.data[32:64]

    def clone(self) -> "Slip21Node":
        return Slip21Node(data=self.data)


if not utils.BITCOIN_ONLY:
    # === Cardano variant ===
    # We want to derive both the normal seed and the Cardano seed together, AND
    # expose a method for Cardano to do the same

    async def derive_and_store_roots(ctx: wire.Context) -> None:
        if not device.is_initialized():
            raise wire.NotInitialized("Device is not initialized")

        if not utils.USE_THD89:
            need_seed = not cache.is_set(cache.APP_COMMON_SEED)
            need_cardano_secret = cache.get(
                cache.APP_COMMON_DERIVE_CARDANO
            ) and not cache.is_set(cache.APP_CARDANO_ICARUS_SECRET)

            if not need_seed and not need_cardano_secret:
                return
            from apps.common import passphrase

            # if not passphrase.is_passphrase_auto_status():
            #     passphrase = await get_passphrase(ctx)
            #     device.set_passphrase_auto_status(False)
            # else:
            #     passphrase = ""

            passphrase_pin_enabled = passphrase.is_passphrase_pin_enabled()
            if not passphrase_pin_enabled:
                passphrase_str = await get_passphrase(ctx)
            else:
                passphrase_str = ""

            if need_seed:
                common_seed = mnemonic.get_seed(passphrase_str, progress_bar=False)
                cache.set(cache.APP_COMMON_SEED, common_seed)

            if need_cardano_secret:
                from apps.cardano.seed import derive_and_store_secrets

                derive_and_store_secrets(passphrase_str)
        else:
            from trezor.crypto import se_thd89

            from apps.common import passphrase

            passphrase_str = ""
            state = se_thd89.get_session_state()
            if not state[0] & 0x80:
                import utime

                session_id = cache.get_session_id()
                session_id = cache.start_session(session_id)
                if session_id is None or session_id == b"":
                    session_id = cache.start_session()
                    utime.sleep_ms(500)
                from apps.common import passphrase

                passphrase_pin_enabled = passphrase.is_passphrase_pin_enabled()
                if not passphrase_pin_enabled:
                    passphrase_str = await get_passphrase(ctx)
                else:
                    passphrase_str = ""

                from trezor.ui.layouts import show_popup
                from trezor.lvglui.i18n import gettext as _, keys as i18n_keys

                await show_popup(_(i18n_keys.TITLE__PLEASE_WAIT), None, timeout_ms=1000)
                mnemonic.get_seed(passphrase_str, progress_bar=False)

                if cache.SESSION_DIRIVE_CARDANO:
                    from apps.cardano.seed import derive_and_store_secrets

                    derive_and_store_secrets(passphrase_str)

    @cache.stored_async(cache.APP_COMMON_SEED)
    async def get_seed(ctx: wire.Context) -> bytes:
        await derive_and_store_roots(ctx)
        common_seed = cache.get(cache.APP_COMMON_SEED)
        if not utils.USE_THD89:
            assert common_seed is not None
            return common_seed
        else:
            return b""

else:
    # === Bitcoin-only variant ===
    # We use the simple version of `get_seed` that never needs to derive anything else.

    @cache.stored_async(cache.APP_COMMON_SEED)
    async def get_seed(ctx: wire.Context) -> bytes:
        if not utils.USE_THD89:
            passphrase_str = await get_passphrase(ctx)
            return mnemonic.get_seed(passphrase_str, progress_bar=False)
        else:
            from trezor.crypto import se_thd89

            state = se_thd89.get_session_state()

            if not state[0] & 0x80:
                from apps.common import passphrase

                passphrase_pin_enabled = passphrase.is_passphrase_pin_enabled()
                if not passphrase_pin_enabled:
                    passphrase_str = await get_passphrase(ctx)
                else:
                    passphrase_str = ""
                return mnemonic.get_seed(passphrase_str, progress_bar=False)
            else:
                return b""


@cache.stored(cache.APP_COMMON_SEED_WITHOUT_PASSPHRASE)
def _get_seed_without_passphrase() -> bytes:
    if not device.is_initialized():
        raise Exception("Device is not initialized")
    return mnemonic.get_seed(progress_bar=False)


def derive_node_without_passphrase(
    path: Bip32Path, curve_name: str = "secp256k1"
) -> bip32.HDNode:
    seed = _get_seed_without_passphrase()
    node = bip32.from_seed(seed, curve_name)
    node.derive_path(path)
    return node


def derive_fido_node_with_se(
    path: Bip32Path, curve_name: str = "nist256p1"
) -> bip32.HDNode:
    from trezor.crypto import se_thd89

    se_thd89.fido_seed()
    node = bip32.HDNode(
        depth=0,
        fingerprint=0,
        child_num=0,
        chain_code=bytearray(32),
        public_key=bytearray(33),
        curve_name=curve_name,
    )
    node.derive_fido_path(path)
    return node


def derive_slip21_node_without_passphrase(path: Slip21Path) -> Slip21Node:
    if utils.USE_THD89:
        from trezor.crypto import se_thd89

        node = Slip21Node(data=se_thd89.slip21_fido_node())
    else:
        seed = _get_seed_without_passphrase()
        node = Slip21Node(seed)
    node.derive_path(path)

    return node


def remove_ed25519_prefix(pubkey: bytes) -> bytes:
    # 0x01 prefix is not part of the actual public key, hence removed
    return pubkey[1:]
