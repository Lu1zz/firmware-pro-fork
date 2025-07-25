from typing import TYPE_CHECKING

from trezor import utils
from trezor.enums import MessageType

if TYPE_CHECKING:
    from trezor.wire import Handler, Msg
    from trezorio import WireInterface


workflow_handlers: dict[int, Handler] = {}


def register(wire_type: int, handler: Handler[Msg]) -> None:
    workflow_handlers[wire_type] = handler


def find_message_handler_module(msg_type: int) -> str:
    """Statically find the appropriate workflow handler.

    For now, new messages must be registered by hand in the if-elif manner below.
    The reason for this is memory fragmentation optimization:
    - using a dict would mean that the whole thing stays in RAM, whereas an if-elif
      sequence is run from flash
    - collecting everything as strings instead of importing directly means that we don't
      need to load any of the modules into memory until we actually need them
    """
    # debug
    if __debug__:
        if msg_type == MessageType.LoadDevice:
            return "apps.debug.load_device"
        if msg_type == MessageType.ResetDevice:
            return "apps.management.reset_device"
        if msg_type == MessageType.RecoveryDevice:
            return "apps.management.recovery_device"
        if msg_type == MessageType.BackupDevice:
            return "apps.management.backup_device"
    # management
    if msg_type == MessageType.WipeDevice:
        return "apps.management.wipe_device"
    if msg_type == MessageType.ApplySettings:
        return "apps.management.apply_settings"
    if msg_type == MessageType.ApplyFlags:
        return "apps.management.apply_flags"
    if msg_type == MessageType.ChangePin:
        return "apps.management.change_pin"
    if msg_type == MessageType.ChangeWipeCode:
        return "apps.management.change_wipe_code"
    elif msg_type == MessageType.GetNonce:
        return "apps.management.get_nonce"
    elif msg_type == MessageType.SESignMessage:
        return "apps.management.se_sign_message"
    elif msg_type == MessageType.RebootToBootloader:
        return "apps.management.reboot_to_bootloader"
    elif msg_type == MessageType.DeviceBackToBoot:
        return "apps.management.reboot_to_bootloader"
    elif msg_type == MessageType.RebootToBoardloader:
        return "apps.management.reboot_to_boardloader"
    elif msg_type == MessageType.ReadSEPublicCert:
        return "apps.management.se_read_cert"

    if utils.MODEL in ("T",) and msg_type == MessageType.SdProtect:
        return "apps.management.sd_protect"
    if utils.MODEL == "T" and msg_type == MessageType.ResourceUpload:
        if utils.EMULATOR:
            raise ValueError
        return "apps.management.upload_res"
    if utils.MODEL == "T" and msg_type == MessageType.ResourceUpdate:
        if utils.EMULATOR:
            raise ValueError
        return "apps.management.update_res"
    if utils.MODEL == "T" and msg_type == MessageType.ListResDir:
        if utils.EMULATOR:
            raise ValueError
        return "apps.management.list_dir"

    # bitcoin
    if msg_type == MessageType.AuthorizeCoinJoin:
        return "apps.bitcoin.authorize_coinjoin"
    if msg_type == MessageType.GetPublicKey:
        return "apps.bitcoin.get_public_key"
    if msg_type == MessageType.GetAddress:
        return "apps.bitcoin.get_address"
    if msg_type == MessageType.GetOwnershipId:
        return "apps.bitcoin.get_ownership_id"
    if msg_type == MessageType.GetOwnershipProof:
        return "apps.bitcoin.get_ownership_proof"
    if msg_type == MessageType.SignTx:
        return "apps.bitcoin.sign_tx"
    if msg_type == MessageType.SignMessage:
        return "apps.bitcoin.sign_message"
    if msg_type == MessageType.VerifyMessage:
        return "apps.bitcoin.verify_message"
    if msg_type == MessageType.SignPsbt:
        return "apps.bitcoin.sign_taproot"

    # misc
    if msg_type == MessageType.GetEntropy:
        return "apps.misc.get_entropy"
    if msg_type == MessageType.SignIdentity:
        return "apps.misc.sign_identity"
    if msg_type == MessageType.GetECDHSessionKey:
        return "apps.misc.get_ecdh_session_key"
    if msg_type == MessageType.CipherKeyValue:
        return "apps.misc.cipher_key_value"
    if msg_type == MessageType.GetFirmwareHash:
        return "apps.misc.get_firmware_hash"

    if not utils.BITCOIN_ONLY:
        if msg_type == MessageType.BatchGetPublickeys:
            return "apps.misc.batch_get_pubkeys"
        if msg_type == MessageType.SetU2FCounter:
            return "apps.management.set_u2f_counter"
        if msg_type == MessageType.GetNextU2FCounter:
            return "apps.management.get_next_u2f_counter"

        # webauthn
        if msg_type == MessageType.WebAuthnListResidentCredentials:
            return "apps.webauthn.list_resident_credentials"
        if msg_type == MessageType.WebAuthnAddResidentCredential:
            return "apps.webauthn.add_resident_credential"
        if msg_type == MessageType.WebAuthnRemoveResidentCredential:
            return "apps.webauthn.remove_resident_credential"

        # ethereum
        if msg_type == MessageType.EthereumGetAddress:
            return "apps.ethereum.get_address"
        if msg_type == MessageType.EthereumGetPublicKey:
            return "apps.ethereum.get_public_key"
        if msg_type == MessageType.EthereumSignTx:
            return "apps.ethereum.sign_tx"
        if msg_type == MessageType.EthereumSignTxEIP1559:
            return "apps.ethereum.sign_tx_eip1559"
        if msg_type == MessageType.EthereumSignMessage:
            return "apps.ethereum.sign_message"
        if msg_type == MessageType.EthereumVerifyMessage:
            return "apps.ethereum.verify_message"
        if msg_type == MessageType.EthereumSignTypedData:
            return "apps.ethereum.sign_typed_data"
        if msg_type == MessageType.EthereumSignTypedHash:
            return "apps.ethereum.sign_typed_data_hash"

        # ethereum onekey
        if msg_type == MessageType.EthereumGetAddressOneKey:
            return "apps.ethereum.onekey.get_address"
        if msg_type == MessageType.EthereumGetPublicKeyOneKey:
            return "apps.ethereum.onekey.get_public_key"
        if msg_type == MessageType.EthereumSignTxOneKey:
            return "apps.ethereum.onekey.sign_tx"
        if msg_type == MessageType.EthereumSignTxEIP1559OneKey:
            return "apps.ethereum.onekey.sign_tx_eip1559"
        if msg_type == MessageType.EthereumSignMessageOneKey:
            return "apps.ethereum.onekey.sign_message"
        if msg_type == MessageType.EthereumVerifyMessageOneKey:
            return "apps.ethereum.onekey.verify_message"
        if msg_type == MessageType.EthereumSignTypedDataOneKey:
            return "apps.ethereum.onekey.sign_typed_data"
        if msg_type == MessageType.EthereumSignTypedHashOneKey:
            return "apps.ethereum.onekey.sign_typed_data_hash"

        # monero
        if msg_type == MessageType.MoneroGetAddress:
            return "apps.monero.get_address"
        if msg_type == MessageType.MoneroGetWatchKey:
            return "apps.monero.get_watch_only"
        if msg_type == MessageType.MoneroTransactionInitRequest:
            return "apps.monero.sign_tx"
        if msg_type == MessageType.MoneroKeyImageExportInitRequest:
            return "apps.monero.key_image_sync"
        if msg_type == MessageType.MoneroGetTxKeyRequest:
            return "apps.monero.get_tx_keys"
        if msg_type == MessageType.MoneroLiveRefreshStartRequest:
            return "apps.monero.live_refresh"
        if __debug__ and msg_type == MessageType.DebugMoneroDiagRequest:
            return "apps.monero.diag"

        # nem
        if msg_type == MessageType.NEMGetAddress:
            return "apps.nem.get_address"
        if msg_type == MessageType.NEMSignTx:
            return "apps.nem.sign_tx"
        # neo
        if msg_type == MessageType.NeoGetAddress:
            return "apps.neo.get_address"
        if msg_type == MessageType.NeoSignTx:
            return "apps.neo.sign_tx"

        # stellar
        if msg_type == MessageType.StellarGetAddress:
            return "apps.stellar.get_address"
        if msg_type == MessageType.StellarSignTx:
            return "apps.stellar.sign_tx"

        # ripple
        if msg_type == MessageType.RippleGetAddress:
            return "apps.ripple.get_address"
        if msg_type == MessageType.RippleSignTx:
            return "apps.ripple.sign_tx"

        # cardano
        if msg_type == MessageType.CardanoGetAddress:
            return "apps.cardano.get_address"
        if msg_type == MessageType.CardanoGetPublicKey:
            return "apps.cardano.get_public_key"
        if msg_type == MessageType.CardanoSignTxInit:
            return "apps.cardano.sign_tx"
        if msg_type == MessageType.CardanoGetNativeScriptHash:
            return "apps.cardano.get_native_script_hash"
        if msg_type == MessageType.CardanoSignMessage:
            return "apps.cardano.sign_message"

        # tezos
        if msg_type == MessageType.TezosGetAddress:
            return "apps.tezos.get_address"
        if msg_type == MessageType.TezosSignTx:
            return "apps.tezos.sign_tx"
        if msg_type == MessageType.TezosGetPublicKey:
            return "apps.tezos.get_public_key"

        # eos
        if msg_type == MessageType.EosGetPublicKey:
            return "apps.eos.get_public_key"
        if msg_type == MessageType.EosSignTx:
            return "apps.eos.sign_tx"

        # binance
        if msg_type == MessageType.BinanceGetAddress:
            return "apps.binance.get_address"
        if msg_type == MessageType.BinanceGetPublicKey:
            return "apps.binance.get_public_key"
        if msg_type == MessageType.BinanceSignTx:
            return "apps.binance.sign_tx"

        # conflux
        if msg_type == MessageType.ConfluxGetAddress:
            return "apps.conflux.get_address"
        if msg_type == MessageType.ConfluxSignTx:
            return "apps.conflux.sign_tx"
        if msg_type == MessageType.ConfluxSignMessage:
            return "apps.conflux.sign_message"
        if msg_type == MessageType.ConfluxSignMessageCIP23:
            return "apps.conflux.sign_message_cip23"

        # ton
        if msg_type == MessageType.TonGetAddress:
            return "apps.ton.get_address"
        if msg_type == MessageType.TonSignMessage:
            return "apps.ton.sign_message"
        if msg_type == MessageType.TonSignProof:
            return "apps.ton.sign_proof"

        # tron
        if msg_type == MessageType.TronGetAddress:
            return "apps.tron.get_address"
        if msg_type == MessageType.TronSignTx:
            return "apps.tron.sign_tx"
        if msg_type == MessageType.TronSignMessage:
            return "apps.tron.sign_message"

        # solana
        if msg_type == MessageType.SolanaGetAddress:
            return "apps.solana.get_address"
        if msg_type == MessageType.SolanaSignTx:
            return "apps.solana.sign_tx"
        if msg_type == MessageType.SolanaSignUnsafeMessage:
            return "apps.solana.sign_unsafe_message"
        if msg_type == MessageType.SolanaSignOffChainMessage:
            return "apps.solana.sign_offchain_message"

        # starcoin
        if msg_type == MessageType.StarcoinGetAddress:
            return "apps.starcoin.get_address"
        if msg_type == MessageType.StarcoinGetPublicKey:
            return "apps.starcoin.get_public_key"
        if msg_type == MessageType.StarcoinSignTx:
            return "apps.starcoin.sign_tx"
        if msg_type == MessageType.StarcoinSignMessage:
            return "apps.starcoin.sign_message"
        if msg_type == MessageType.StarcoinVerifyMessage:
            return "apps.starcoin.verify_message"

        # near
        if msg_type == MessageType.NearGetAddress:
            return "apps.near.get_address"
        if msg_type == MessageType.NearSignTx:
            return "apps.near.sign_tx"
        # aptos
        if msg_type == MessageType.AptosGetAddress:
            return "apps.aptos.get_address"
        if msg_type == MessageType.AptosSignTx:
            return "apps.aptos.sign_tx"
        if msg_type == MessageType.AptosSignMessage:
            return "apps.aptos.sign_message"

        # algo
        if msg_type == MessageType.AlgorandGetAddress:
            return "apps.algorand.get_address"
        if msg_type == MessageType.AlgorandSignTx:
            return "apps.algorand.sign_tx"

        # polkadot
        if msg_type == MessageType.PolkadotGetAddress:
            return "apps.polkadot.get_address"
        if msg_type == MessageType.PolkadotSignTx:
            return "apps.polkadot.sign_tx"

        # sui
        if msg_type == MessageType.SuiGetAddress:
            return "apps.sui.get_address"
        if msg_type == MessageType.SuiSignTx:
            return "apps.sui.sign_tx"
        if msg_type == MessageType.SuiSignMessage:
            return "apps.sui.sign_message"

        # filecoin
        if msg_type == MessageType.FilecoinGetAddress:
            return "apps.filecoin.get_address"
        if msg_type == MessageType.FilecoinSignTx:
            return "apps.filecoin.sign_tx"

        # cosmos
        if msg_type == MessageType.CosmosGetAddress:
            return "apps.cosmos.get_address"
        if msg_type == MessageType.CosmosSignTx:
            return "apps.cosmos.sign_tx"

        # kaspa
        if msg_type == MessageType.KaspaGetAddress:
            return "apps.kaspa.get_address"
        if msg_type == MessageType.KaspaSignTx:
            return "apps.kaspa.sign_tx"

        # nexa
        if msg_type == MessageType.NexaGetAddress:
            return "apps.nexa.get_address"
        if msg_type == MessageType.NexaSignTx:
            return "apps.nexa.sign_tx"
        # nervos
        if msg_type == MessageType.NervosGetAddress:
            return "apps.nervos.get_address"
        if msg_type == MessageType.NervosSignTx:
            return "apps.nervos.sign_tx"

        if msg_type == MessageType.NostrGetPublicKey:
            return "apps.nostr.get_public_key"
        if msg_type == MessageType.NostrSignEvent:
            return "apps.nostr.sign_event"
        if msg_type == MessageType.NostrEncryptMessage:
            return "apps.nostr.encrypt"
        if msg_type == MessageType.NostrDecryptMessage:
            return "apps.nostr.decrypt"
        if msg_type == MessageType.NostrSignSchnorr:
            return "apps.nostr.schnorr"

        if msg_type == MessageType.LnurlAuth:
            return "apps.lnurl.auth"

        # scdo
        if msg_type == MessageType.ScdoGetAddress:
            return "apps.scdo.get_address"
        if msg_type == MessageType.ScdoSignTx:
            return "apps.scdo.sign_tx"
        if msg_type == MessageType.ScdoSignMessage:
            return "apps.scdo.sign_message"

        # alephium
        if msg_type == MessageType.AlephiumGetAddress:
            return "apps.alephium.get_address"
        if msg_type == MessageType.AlephiumSignTx:
            return "apps.alephium.sign_tx"
        if msg_type == MessageType.AlephiumSignMessage:
            return "apps.alephium.sign_message"

        # benfen
        if msg_type == MessageType.BenfenGetAddress:
            return "apps.benfen.get_address"
        if msg_type == MessageType.BenfenSignTx:
            return "apps.benfen.sign_tx"
        if msg_type == MessageType.BenfenSignMessage:
            return "apps.benfen.sign_message"

    raise ValueError


def find_registered_handler(iface: WireInterface, msg_type: int) -> Handler | None:
    if msg_type in workflow_handlers:
        return workflow_handlers[msg_type]

    try:
        modname = find_message_handler_module(msg_type)
        handler_name = modname[modname.rfind(".") + 1 :]
        module = __import__(modname, None, None, (handler_name,), 0)
        handler = getattr(module, handler_name)

        if iface is not None and _is_address_derivation_message(msg_type):
            return _wrap_with_version_check(handler)

        return handler
    except ValueError:
        return None


def _is_address_derivation_message(msg_type: int) -> bool:
    return msg_type in (
        MessageType.GetAddress,
        MessageType.GetPublicKey,
        MessageType.EthereumGetAddress,
        MessageType.EthereumGetAddressOneKey,
        MessageType.MoneroGetAddress,
        MessageType.NEMGetAddress,
        MessageType.NeoGetAddress,
        MessageType.StellarGetAddress,
        MessageType.RippleGetAddress,
        MessageType.CardanoGetAddress,
        MessageType.TezosGetAddress,
        MessageType.BinanceGetAddress,
        MessageType.ConfluxGetAddress,
        MessageType.TonGetAddress,
        MessageType.TronGetAddress,
        MessageType.SolanaGetAddress,
        MessageType.StarcoinGetAddress,
        MessageType.NearGetAddress,
        MessageType.AptosGetAddress,
        MessageType.AlgorandGetAddress,
        MessageType.PolkadotGetAddress,
        MessageType.SuiGetAddress,
        MessageType.FilecoinGetAddress,
        MessageType.CosmosGetAddress,
        MessageType.KaspaGetAddress,
        MessageType.NexaGetAddress,
        MessageType.NervosGetAddress,
        MessageType.ScdoGetAddress,
        MessageType.AlephiumGetAddress,
        MessageType.BenfenGetAddress,
        # Add other GetPublicKey variants
        MessageType.BinanceGetPublicKey,
        MessageType.CardanoGetPublicKey,
        MessageType.EthereumGetPublicKey,
        MessageType.EthereumGetPublicKeyOneKey,
        MessageType.TezosGetPublicKey,
        MessageType.StarcoinGetPublicKey,
        # MessageType.EOSGetPublicKey,
        MessageType.NostrGetPublicKey,
    )


def _wrap_with_version_check(handler):
    async def wrapper(ctx, msg):
        # Execute the original handler
        result = await handler(ctx, msg)
        from apps.base import check_version_compatibility

        check_version_compatibility()
        return result

    return wrapper
