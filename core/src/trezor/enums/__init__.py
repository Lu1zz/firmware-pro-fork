from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from enum import IntEnum

    class AptosTransactionType(IntEnum):
        STANDARD = 0
        WITH_DATA = 1

    class BinanceOrderType(IntEnum):
        OT_UNKNOWN = 0
        MARKET = 1
        LIMIT = 2
        OT_RESERVED = 3

    class BinanceOrderSide(IntEnum):
        SIDE_UNKNOWN = 0
        BUY = 1
        SELL = 2

    class BinanceTimeInForce(IntEnum):
        TIF_UNKNOWN = 0
        GTE = 1
        TIF_RESERVED = 2
        IOC = 3

    class MessageType(IntEnum):
        Initialize = 0
        Ping = 1
        Success = 2
        Failure = 3
        ChangePin = 4
        WipeDevice = 5
        GetEntropy = 9
        Entropy = 10
        LoadDevice = 13
        ResetDevice = 14
        SetBusy = 16
        Features = 17
        PinMatrixRequest = 18
        PinMatrixAck = 19
        Cancel = 20
        LockDevice = 24
        ApplySettings = 25
        ButtonRequest = 26
        ButtonAck = 27
        ApplyFlags = 28
        GetNonce = 31
        Nonce = 33
        BackupDevice = 34
        EntropyRequest = 35
        EntropyAck = 36
        PassphraseRequest = 41
        PassphraseAck = 42
        RecoveryDevice = 45
        WordRequest = 46
        WordAck = 47
        GetFeatures = 55
        SdProtect = 79
        ChangeWipeCode = 82
        EndSession = 83
        DoPreauthorized = 84
        PreauthorizedRequest = 85
        CancelAuthorization = 86
        RebootToBootloader = 87
        GetFirmwareHash = 88
        FirmwareHash = 89
        UnlockPath = 93
        UnlockedPathRequest = 94
        SetU2FCounter = 63
        GetNextU2FCounter = 80
        NextU2FCounter = 81
        Deprecated_PassphraseStateRequest = 77
        Deprecated_PassphraseStateAck = 78
        FirmwareErase = 6
        FirmwareUpload = 7
        FirmwareRequest = 8
        FirmwareErase_ex = 16
        SelfTest = 32
        Reboot = 30000
        FirmwareUpdateEmmc = 30001
        GetPublicKey = 11
        PublicKey = 12
        SignTx = 15
        TxRequest = 21
        TxAck = 22
        GetAddress = 29
        Address = 30
        TxAckPaymentRequest = 37
        SignMessage = 38
        VerifyMessage = 39
        MessageSignature = 40
        GetOwnershipId = 43
        OwnershipId = 44
        GetOwnershipProof = 49
        OwnershipProof = 50
        AuthorizeCoinJoin = 51
        SignPsbt = 10052
        SignedPsbt = 10053
        CipherKeyValue = 23
        CipheredKeyValue = 48
        SignIdentity = 53
        SignedIdentity = 54
        GetECDHSessionKey = 61
        ECDHSessionKey = 62
        CosiCommit = 71
        CosiCommitment = 72
        CosiSign = 73
        CosiSignature = 74
        BatchGetPublickeys = 10016
        EcdsaPublicKeys = 10017
        DebugLinkDecision = 100
        DebugLinkGetState = 101
        DebugLinkState = 102
        DebugLinkStop = 103
        DebugLinkLog = 104
        DebugLinkMemoryRead = 110
        DebugLinkMemory = 111
        DebugLinkMemoryWrite = 112
        DebugLinkFlashErase = 113
        DebugLinkLayout = 9001
        DebugLinkReseedRandom = 9002
        DebugLinkRecordScreen = 9003
        DebugLinkEraseSdCard = 9005
        DebugLinkWatchLayout = 9006
        EmmcFixPermission = 30100
        EmmcPath = 30101
        EmmcPathInfo = 30102
        EmmcFile = 30103
        EmmcFileRead = 30104
        EmmcFileWrite = 30105
        EmmcFileDelete = 30106
        EmmcDir = 30107
        EmmcDirList = 30108
        EmmcDirMake = 30109
        EmmcDirRemove = 30110
        EthereumGetPublicKey = 450
        EthereumPublicKey = 451
        EthereumGetAddress = 56
        EthereumAddress = 57
        EthereumSignTx = 58
        EthereumSignTxEIP1559 = 452
        EthereumTxRequest = 59
        EthereumTxAck = 60
        EthereumSignMessage = 64
        EthereumVerifyMessage = 65
        EthereumMessageSignature = 66
        EthereumSignTypedData = 464
        EthereumTypedDataStructRequest = 465
        EthereumTypedDataStructAck = 466
        EthereumTypedDataValueRequest = 467
        EthereumTypedDataValueAck = 468
        EthereumTypedDataSignature = 469
        EthereumSignTypedHash = 470
        EthereumGetPublicKeyOneKey = 20100
        EthereumPublicKeyOneKey = 20101
        EthereumGetAddressOneKey = 20102
        EthereumAddressOneKey = 20103
        EthereumSignTxOneKey = 20104
        EthereumSignTxEIP1559OneKey = 20105
        EthereumTxRequestOneKey = 20106
        EthereumTxAckOneKey = 20107
        EthereumSignMessageOneKey = 20108
        EthereumVerifyMessageOneKey = 20109
        EthereumMessageSignatureOneKey = 20110
        EthereumSignTypedDataOneKey = 20111
        EthereumTypedDataStructRequestOneKey = 20112
        EthereumTypedDataStructAckOneKey = 20113
        EthereumTypedDataValueRequestOneKey = 20114
        EthereumTypedDataValueAckOneKey = 20115
        EthereumTypedDataSignatureOneKey = 20116
        EthereumSignTypedHashOneKey = 20117
        EthereumGnosisSafeTxAck = 20118
        EthereumGnosisSafeTxRequest = 20119
        NEMGetAddress = 67
        NEMAddress = 68
        NEMSignTx = 69
        NEMSignedTx = 70
        NEMDecryptMessage = 75
        NEMDecryptedMessage = 76
        TezosGetAddress = 150
        TezosAddress = 151
        TezosSignTx = 152
        TezosSignedTx = 153
        TezosGetPublicKey = 154
        TezosPublicKey = 155
        StellarSignTx = 202
        StellarTxOpRequest = 203
        StellarGetAddress = 207
        StellarAddress = 208
        StellarCreateAccountOp = 210
        StellarPaymentOp = 211
        StellarPathPaymentStrictReceiveOp = 212
        StellarManageSellOfferOp = 213
        StellarCreatePassiveSellOfferOp = 214
        StellarSetOptionsOp = 215
        StellarChangeTrustOp = 216
        StellarAllowTrustOp = 217
        StellarAccountMergeOp = 218
        StellarManageDataOp = 220
        StellarBumpSequenceOp = 221
        StellarManageBuyOfferOp = 222
        StellarPathPaymentStrictSendOp = 223
        StellarSignedTx = 230
        CardanoGetPublicKey = 305
        CardanoPublicKey = 306
        CardanoGetAddress = 307
        CardanoAddress = 308
        CardanoTxItemAck = 313
        CardanoTxAuxiliaryDataSupplement = 314
        CardanoTxWitnessRequest = 315
        CardanoTxWitnessResponse = 316
        CardanoTxHostAck = 317
        CardanoTxBodyHash = 318
        CardanoSignTxFinished = 319
        CardanoSignTxInit = 320
        CardanoTxInput = 321
        CardanoTxOutput = 322
        CardanoAssetGroup = 323
        CardanoToken = 324
        CardanoTxCertificate = 325
        CardanoTxWithdrawal = 326
        CardanoTxAuxiliaryData = 327
        CardanoPoolOwner = 328
        CardanoPoolRelayParameters = 329
        CardanoGetNativeScriptHash = 330
        CardanoNativeScriptHash = 331
        CardanoTxMint = 332
        CardanoTxCollateralInput = 333
        CardanoTxRequiredSigner = 334
        CardanoTxInlineDatumChunk = 335
        CardanoTxReferenceScriptChunk = 336
        CardanoTxReferenceInput = 337
        CardanoSignMessage = 350
        CardanoMessageSignature = 351
        RippleGetAddress = 400
        RippleAddress = 401
        RippleSignTx = 402
        RippleSignedTx = 403
        MoneroTransactionInitRequest = 501
        MoneroTransactionInitAck = 502
        MoneroTransactionSetInputRequest = 503
        MoneroTransactionSetInputAck = 504
        MoneroTransactionInputViniRequest = 507
        MoneroTransactionInputViniAck = 508
        MoneroTransactionAllInputsSetRequest = 509
        MoneroTransactionAllInputsSetAck = 510
        MoneroTransactionSetOutputRequest = 511
        MoneroTransactionSetOutputAck = 512
        MoneroTransactionAllOutSetRequest = 513
        MoneroTransactionAllOutSetAck = 514
        MoneroTransactionSignInputRequest = 515
        MoneroTransactionSignInputAck = 516
        MoneroTransactionFinalRequest = 517
        MoneroTransactionFinalAck = 518
        MoneroKeyImageExportInitRequest = 530
        MoneroKeyImageExportInitAck = 531
        MoneroKeyImageSyncStepRequest = 532
        MoneroKeyImageSyncStepAck = 533
        MoneroKeyImageSyncFinalRequest = 534
        MoneroKeyImageSyncFinalAck = 535
        MoneroGetAddress = 540
        MoneroAddress = 541
        MoneroGetWatchKey = 542
        MoneroWatchKey = 543
        DebugMoneroDiagRequest = 546
        DebugMoneroDiagAck = 547
        MoneroGetTxKeyRequest = 550
        MoneroGetTxKeyAck = 551
        MoneroLiveRefreshStartRequest = 552
        MoneroLiveRefreshStartAck = 553
        MoneroLiveRefreshStepRequest = 554
        MoneroLiveRefreshStepAck = 555
        MoneroLiveRefreshFinalRequest = 556
        MoneroLiveRefreshFinalAck = 557
        EosGetPublicKey = 600
        EosPublicKey = 601
        EosSignTx = 602
        EosTxActionRequest = 603
        EosTxActionAck = 604
        EosSignedTx = 605
        BinanceGetAddress = 700
        BinanceAddress = 701
        BinanceGetPublicKey = 702
        BinancePublicKey = 703
        BinanceSignTx = 704
        BinanceTxRequest = 705
        BinanceTransferMsg = 706
        BinanceOrderMsg = 707
        BinanceCancelMsg = 708
        BinanceSignedTx = 709
        StarcoinGetAddress = 10300
        StarcoinAddress = 10301
        StarcoinGetPublicKey = 10302
        StarcoinPublicKey = 10303
        StarcoinSignTx = 10304
        StarcoinSignedTx = 10305
        StarcoinSignMessage = 10306
        StarcoinMessageSignature = 10307
        StarcoinVerifyMessage = 10308
        ConfluxGetAddress = 10112
        ConfluxAddress = 10113
        ConfluxSignTx = 10114
        ConfluxTxRequest = 10115
        ConfluxTxAck = 10116
        ConfluxSignMessage = 10117
        ConfluxSignMessageCIP23 = 10118
        ConfluxMessageSignature = 10119
        TronGetAddress = 10501
        TronAddress = 10502
        TronSignTx = 10503
        TronSignedTx = 10504
        TronSignMessage = 10505
        TronMessageSignature = 10506
        NearGetAddress = 10701
        NearAddress = 10702
        NearSignTx = 10703
        NearSignedTx = 10704
        AptosGetAddress = 10600
        AptosAddress = 10601
        AptosSignTx = 10602
        AptosSignedTx = 10603
        AptosSignMessage = 10604
        AptosMessageSignature = 10605
        WebAuthnListResidentCredentials = 800
        WebAuthnCredentials = 801
        WebAuthnAddResidentCredential = 802
        WebAuthnRemoveResidentCredential = 803
        SolanaGetAddress = 10100
        SolanaAddress = 10101
        SolanaSignTx = 10102
        SolanaSignedTx = 10103
        SolanaSignOffChainMessage = 10104
        SolanaMessageSignature = 10105
        SolanaSignUnsafeMessage = 10106
        CosmosGetAddress = 10800
        CosmosAddress = 10801
        CosmosSignTx = 10802
        CosmosSignedTx = 10803
        AlgorandGetAddress = 10900
        AlgorandAddress = 10901
        AlgorandSignTx = 10902
        AlgorandSignedTx = 10903
        PolkadotGetAddress = 11000
        PolkadotAddress = 11001
        PolkadotSignTx = 11002
        PolkadotSignedTx = 11003
        SuiGetAddress = 11100
        SuiAddress = 11101
        SuiSignTx = 11102
        SuiSignedTx = 11103
        SuiSignMessage = 11104
        SuiMessageSignature = 11105
        SuiTxRequest = 11106
        SuiTxAck = 11107
        FilecoinGetAddress = 11200
        FilecoinAddress = 11201
        FilecoinSignTx = 11202
        FilecoinSignedTx = 11203
        KaspaGetAddress = 11300
        KaspaAddress = 11301
        KaspaSignTx = 11302
        KaspaSignedTx = 11303
        KaspaTxInputRequest = 11304
        KaspaTxInputAck = 11305
        NexaGetAddress = 11400
        NexaAddress = 11401
        NexaSignTx = 11402
        NexaSignedTx = 11403
        NexaTxInputRequest = 11404
        NexaTxInputAck = 11405
        NostrGetPublicKey = 11500
        NostrPublicKey = 11501
        NostrSignEvent = 11502
        NostrSignedEvent = 11503
        NostrEncryptMessage = 11504
        NostrEncryptedMessage = 11505
        NostrDecryptMessage = 11506
        NostrDecryptedMessage = 11507
        NostrSignSchnorr = 11508
        NostrSignedSchnorr = 11509
        LnurlAuth = 11600
        LnurlAuthResp = 11601
        NervosGetAddress = 11701
        NervosAddress = 11702
        NervosSignTx = 11703
        NervosSignedTx = 11704
        NervosTxRequest = 11705
        NervosTxAck = 11706
        TonGetAddress = 11901
        TonAddress = 11902
        TonSignMessage = 11903
        TonSignedMessage = 11904
        TonSignProof = 11905
        TonSignedProof = 11906
        TonTxAck = 11907
        ScdoGetAddress = 12001
        ScdoAddress = 12002
        ScdoSignTx = 12003
        ScdoSignedTx = 12004
        ScdoTxAck = 12005
        ScdoSignMessage = 12006
        ScdoSignedMessage = 12007
        AlephiumGetAddress = 12101
        AlephiumAddress = 12102
        AlephiumSignTx = 12103
        AlephiumSignedTx = 12104
        AlephiumTxRequest = 12105
        AlephiumTxAck = 12106
        AlephiumBytecodeRequest = 12107
        AlephiumBytecodeAck = 12108
        AlephiumSignMessage = 12109
        AlephiumMessageSignature = 12110
        BenfenGetAddress = 12201
        BenfenAddress = 12202
        BenfenSignTx = 12203
        BenfenSignedTx = 12204
        BenfenSignMessage = 12205
        BenfenMessageSignature = 12206
        BenfenTxRequest = 12207
        BenfenTxAck = 12208
        NeoGetAddress = 12301
        NeoAddress = 12302
        NeoSignTx = 12303
        NeoSignedTx = 12304
        DeviceBackToBoot = 903
        RebootToBoardloader = 904
        DeviceInfoSettings = 10001
        GetDeviceInfo = 10002
        DeviceInfo = 10003
        ReadSEPublicKey = 10004
        SEPublicKey = 10005
        WriteSEPublicCert = 10006
        ReadSEPublicCert = 10007
        SEPublicCert = 10008
        SESignMessage = 10012
        SEMessageSignature = 10013
        ResourceUpload = 10018
        ZoomRequest = 10019
        ResourceRequest = 10020
        ResourceAck = 10021
        ResourceUpdate = 10022
        ListResDir = 10023
        FileInfoList = 10024
        OnekeyGetFeatures = 10025
        OnekeyFeatures = 10026
        WriteSEPrivateKey = 10027
        GetPassphraseState = 10028
        PassphraseState = 10029
        UnLockDevice = 10030
        UnLockDeviceResponse = 10031

    class FailureType(IntEnum):
        UnexpectedMessage = 1
        ButtonExpected = 2
        DataError = 3
        ActionCancelled = 4
        PinExpected = 5
        PinCancelled = 6
        PinInvalid = 7
        InvalidSignature = 8
        ProcessError = 9
        NotEnoughFunds = 10
        NotInitialized = 11
        PinMismatch = 12
        WipeCodeMismatch = 13
        InvalidSession = 14
        FirmwareError = 99

    class ButtonRequestType(IntEnum):
        Other = 1
        FeeOverThreshold = 2
        ConfirmOutput = 3
        ResetDevice = 4
        ConfirmWord = 5
        WipeDevice = 6
        ProtectCall = 7
        SignTx = 8
        FirmwareCheck = 9
        Address = 10
        PublicKey = 11
        MnemonicWordCount = 12
        MnemonicInput = 13
        _Deprecated_ButtonRequest_PassphraseType = 14
        UnknownDerivationPath = 15
        RecoveryHomepage = 16
        Success = 17
        Warning = 18
        PassphraseEntry = 19
        PinEntry = 20
        AttachPin = 8000

    class PinMatrixRequestType(IntEnum):
        Current = 1
        NewFirst = 2
        NewSecond = 3
        WipeCodeFirst = 4
        WipeCodeSecond = 5

    class InputScriptType(IntEnum):
        SPENDADDRESS = 0
        SPENDMULTISIG = 1
        EXTERNAL = 2
        SPENDWITNESS = 3
        SPENDP2SHWITNESS = 4
        SPENDTAPROOT = 5

    class OutputScriptType(IntEnum):
        PAYTOADDRESS = 0
        PAYTOSCRIPTHASH = 1
        PAYTOMULTISIG = 2
        PAYTOOPRETURN = 3
        PAYTOWITNESS = 4
        PAYTOP2SHWITNESS = 5
        PAYTOTAPROOT = 6

    class DecredStakingSpendType(IntEnum):
        SSGen = 0
        SSRTX = 1

    class AmountUnit(IntEnum):
        BITCOIN = 0
        MILLIBITCOIN = 1
        MICROBITCOIN = 2
        SATOSHI = 3

    class RequestType(IntEnum):
        TXINPUT = 0
        TXOUTPUT = 1
        TXMETA = 2
        TXFINISHED = 3
        TXEXTRADATA = 4
        TXORIGINPUT = 5
        TXORIGOUTPUT = 6
        TXPAYMENTREQ = 7

    class CardanoDerivationType(IntEnum):
        LEDGER = 0
        ICARUS = 1
        ICARUS_TREZOR = 2

    class CardanoAddressType(IntEnum):
        BASE = 0
        BASE_SCRIPT_KEY = 1
        BASE_KEY_SCRIPT = 2
        BASE_SCRIPT_SCRIPT = 3
        POINTER = 4
        POINTER_SCRIPT = 5
        ENTERPRISE = 6
        ENTERPRISE_SCRIPT = 7
        BYRON = 8
        REWARD = 14
        REWARD_SCRIPT = 15

    class CardanoNativeScriptType(IntEnum):
        PUB_KEY = 0
        ALL = 1
        ANY = 2
        N_OF_K = 3
        INVALID_BEFORE = 4
        INVALID_HEREAFTER = 5

    class CardanoNativeScriptHashDisplayFormat(IntEnum):
        HIDE = 0
        BECH32 = 1
        POLICY_ID = 2

    class CardanoTxOutputSerializationFormat(IntEnum):
        ARRAY_LEGACY = 0
        MAP_BABBAGE = 1

    class CardanoCertificateType(IntEnum):
        STAKE_REGISTRATION = 0
        STAKE_DEREGISTRATION = 1
        STAKE_DELEGATION = 2
        STAKE_POOL_REGISTRATION = 3
        STAKE_REGISTRATION_CONWAY = 7
        STAKE_DEREGISTRATION_CONWAY = 8
        VOTE_DELEGATION = 9

    class CardanoDRepType(IntEnum):
        KEY_HASH = 0
        SCRIPT_HASH = 1
        ABSTAIN = 2
        NO_CONFIDENCE = 3

    class CardanoPoolRelayType(IntEnum):
        SINGLE_HOST_IP = 0
        SINGLE_HOST_NAME = 1
        MULTIPLE_HOST_NAME = 2

    class CardanoTxAuxiliaryDataSupplementType(IntEnum):
        NONE = 0
        CVOTE_REGISTRATION_SIGNATURE = 1

    class CardanoCVoteRegistrationFormat(IntEnum):
        CIP15 = 0
        CIP36 = 1

    class CardanoTxSigningMode(IntEnum):
        ORDINARY_TRANSACTION = 0
        POOL_REGISTRATION_AS_OWNER = 1
        MULTISIG_TRANSACTION = 2
        PLUTUS_TRANSACTION = 3

    class CardanoTxWitnessType(IntEnum):
        BYRON_WITNESS = 0
        SHELLEY_WITNESS = 1

    class BackupType(IntEnum):
        Bip39 = 0
        Slip39_Basic = 1
        Slip39_Advanced = 2
        Slip39_Single_Extendable = 3
        Slip39_Basic_Extendable = 4
        Slip39_Advanced_Extendable = 5

    class SafetyCheckLevel(IntEnum):
        Strict = 0
        PromptAlways = 1
        PromptTemporarily = 2

    class OneKeyDeviceType(IntEnum):
        CLASSIC = 0
        CLASSIC1S = 1
        MINI = 2
        TOUCH = 3
        PRO = 5

    class OneKeySeType(IntEnum):
        THD89 = 0
        SE608A = 1

    class OneKeySEState(IntEnum):
        BOOT = 0
        APP = 1

    class Capability(IntEnum):
        Bitcoin = 1
        Bitcoin_like = 2
        Binance = 3
        Cardano = 4
        Crypto = 5
        EOS = 6
        Ethereum = 7
        Lisk = 8
        Monero = 9
        NEM = 10
        Ripple = 11
        Stellar = 12
        Tezos = 13
        U2F = 14
        Shamir = 15
        ShamirGroups = 16
        PassphraseEntry = 17
        AttachToPin = 18

    class SdProtectOperationType(IntEnum):
        DISABLE = 0
        ENABLE = 1
        REFRESH = 2

    class RecoveryDeviceType(IntEnum):
        ScrambledWords = 0
        Matrix = 1

    class WordRequestType(IntEnum):
        Plain = 0
        Matrix9 = 1
        Matrix6 = 2

    class ResourceType(IntEnum):
        WallPaper = 0
        Nft = 1

    class DebugSwipeDirection(IntEnum):
        UP = 0
        DOWN = 1
        LEFT = 2
        RIGHT = 3

    class DebugButton(IntEnum):
        NO = 0
        YES = 1
        INFO = 2

    class EthereumDefinitionType(IntEnum):
        NETWORK = 0
        TOKEN = 1

    class EthereumGnosisSafeTxOperation(IntEnum):
        CALL = 0
        DELEGATE_CALL = 1

    class EthereumDataTypeOneKey(IntEnum):
        UINT = 1
        INT = 2
        BYTES = 3
        STRING = 4
        BOOL = 5
        ADDRESS = 6
        ARRAY = 7
        STRUCT = 8

    class EthereumDataType(IntEnum):
        UINT = 1
        INT = 2
        BYTES = 3
        STRING = 4
        BOOL = 5
        ADDRESS = 6
        ARRAY = 7
        STRUCT = 8

    class MoneroNetworkType(IntEnum):
        MAINNET = 0
        TESTNET = 1
        STAGENET = 2
        FAKECHAIN = 3

    class NEMMosaicLevy(IntEnum):
        MosaicLevy_Absolute = 1
        MosaicLevy_Percentile = 2

    class NEMSupplyChangeType(IntEnum):
        SupplyChange_Increase = 1
        SupplyChange_Decrease = 2

    class NEMModificationType(IntEnum):
        CosignatoryModification_Add = 1
        CosignatoryModification_Delete = 2

    class NEMImportanceTransferMode(IntEnum):
        ImportanceTransfer_Activate = 1
        ImportanceTransfer_Deactivate = 2

    class SolanaOffChainMessageVersion(IntEnum):
        MESSAGE_VERSION_0 = 0

    class SolanaOffChainMessageFormat(IntEnum):
        V0_RESTRICTED_ASCII = 0
        V0_LIMITED_UTF8 = 1

    class StellarAssetType(IntEnum):
        NATIVE = 0
        ALPHANUM4 = 1
        ALPHANUM12 = 2

    class StellarMemoType(IntEnum):
        NONE = 0
        TEXT = 1
        ID = 2
        HASH = 3
        RETURN = 4

    class StellarSignerType(IntEnum):
        ACCOUNT = 0
        PRE_AUTH = 1
        HASH = 2

    class TezosContractType(IntEnum):
        Implicit = 0
        Originated = 1

    class TezosBallotType(IntEnum):
        Yay = 0
        Nay = 1
        Pass = 2

    class TonWalletVersion(IntEnum):
        V4R2 = 3

    class TonWorkChain(IntEnum):
        BASECHAIN = 0
        MASTERCHAIN = 1

    class TronResourceCode(IntEnum):
        BANDWIDTH = 0
        ENERGY = 1
        TRON_POWER = 2
