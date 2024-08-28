from typing import TYPE_CHECKING

from .crypto_coin_info import Bitcoin, CryptoCoinInfo, Ethereum, MainNet
from .crypto_hd_key import CryptoHDKey
from .crypto_key_path import CryptoKeyPath

if TYPE_CHECKING:
    from trezor.messages import PublicKey

BTC_LEGACY_PREFIX: str = "m/44'/0'/0'"
BTC_SEGWIT_PREFIX: str = "m/49'/0'/0'"
BTC_NATIVE_SEGWIT_PREFIX: str = "m/84'/0'/0'"
BTC_TAPROOT_PREFIX: str = "m/86'/0'/0'"
ETH_STANDARD_PREFIX: str = "m/44'/60'/0'"


def generate_HDKey(
    pubkey: PublicKey,
    coin_info: CryptoCoinInfo,
    path: str,
    root_fingerprint: int | None,
    name: str | None,
    note: str | None,
) -> CryptoHDKey:
    hdkey = CryptoHDKey()
    assert root_fingerprint is not None, "Root fingerprint should not be None"
    hdkey.new_extended_key(
        False,
        pubkey.node.public_key,
        pubkey.node.chain_code,
        coin_info,
        CryptoKeyPath.from_path(path, root_fingerprint),
        None,
        pubkey.node.fingerprint,
        name,
        note,
    )
    return hdkey


def reveal_name(ctx, root_fingerprint: int) -> str:
    from apps.common import passphrase

    name = "OneKey Pro"
    if passphrase.is_enabled() and ctx.passphrase:
        from binascii import hexlify
        from trezor.crypto.hashlib import blake2b

        state = blake2b(
            data=int.to_bytes(root_fingerprint, 4, "big"),
            outlen=4,
            personal=b"OKPassphraseUsed",
        ).digest()
        name = f"OneKey Pro-{hexlify(state).decode()}"
    return name


def generate_hdkey_ETHStandard(
    ctx, pubkey: PublicKey, eth_only: bool = True
) -> CryptoHDKey:
    if eth_only:
        assert (
            pubkey.root_fingerprint is not None
        ), "Root fingerprint should not be None"
        name = reveal_name(ctx, pubkey.root_fingerprint)
    else:
        name = None
    hdkey = generate_HDKey(
        pubkey,
        CryptoCoinInfo(Ethereum, MainNet),
        ETH_STANDARD_PREFIX,
        pubkey.root_fingerprint,
        name,
        "account.standard",
    )
    return hdkey


def generate_hdkey_BTCLegacy(pubkey: PublicKey) -> CryptoHDKey:
    return generate_HDKey(
        pubkey,
        CryptoCoinInfo(Bitcoin, MainNet),
        BTC_LEGACY_PREFIX,
        pubkey.root_fingerprint,
        None,
        "account.btc_legacy",
    )


def generate_hdkey_BTCSegWit(pubkey: PublicKey) -> CryptoHDKey:
    return generate_HDKey(
        pubkey,
        CryptoCoinInfo(Bitcoin, MainNet),
        BTC_SEGWIT_PREFIX,
        pubkey.root_fingerprint,
        None,
        "account.btc_segwit",
    )


def generate_hdkey_BTCNativeSegWit(pubkey: PublicKey) -> CryptoHDKey:
    return generate_HDKey(
        pubkey,
        CryptoCoinInfo(Bitcoin, MainNet),
        BTC_NATIVE_SEGWIT_PREFIX,
        pubkey.root_fingerprint,
        None,
        "account.btc_native_segwit",
    )


def generate_hdkey_BTCTaproot(pubkey: PublicKey) -> CryptoHDKey:
    return generate_HDKey(
        pubkey,
        CryptoCoinInfo(Bitcoin, MainNet),
        BTC_TAPROOT_PREFIX,
        pubkey.root_fingerprint,
        None,
        "account.btc_taproot",
    )