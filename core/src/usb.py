from micropython import const

import storage
from trezor import io, utils


def get_product_id():
    import storage.device

    return 0x53C1 if storage.device.is_trezor_compatible() else 0x4F4B


active_iface = []

usb21_enabled = False if __debug__ else True


def init() -> io.USB:
    bus = io.USB(
        vendor_id=0x1209,
        product_id=get_product_id(),
        release_num=0x0200,
        manufacturer="OneKey",
        product="OneKey Pro",
        interface="OneKey Interface",
        usb21_landing=False,
        usb21_enabled=usb21_enabled,
    )
    return bus


bus = init()
UDP_PORT = 0
WIRE_PORT_OFFSET = const(0)
DEBUGLINK_PORT_OFFSET = const(1)
WEBAUTHN_PORT_OFFSET = const(2)
VCP_PORT_OFFSET = const(3)

if utils.EMULATOR:
    import uos

    UDP_PORT = int(uos.getenv("ONEKEY_UDP_PORT") or "54935")

_iface_iter = iter(range(5))

ENABLE_IFACE_DEBUG = __debug__
ENABLE_IFACE_WEBAUTHN = storage.device.is_fido_enabled()
ENABLE_IFACE_VCP = __debug__

# interface used for trezor wire protocol
id_wire = next(_iface_iter)
iface_wire = io.WebUSB(
    iface_num=id_wire,
    ep_in=0x81 + id_wire,
    ep_out=0x01 + id_wire,
    emu_port=UDP_PORT + WIRE_PORT_OFFSET,
)
bus.add(iface_wire)
active_iface.append(iface_wire)

# XXXXXXXXXXXXXXXXXXX
#
# We want the following branches present only in their respective firmwares. To achieve
# that, we are taking advantage of the upy compiler static optimization: when an
# if-expression statically evaluates to False, the branch is excluded from the bytecode.
# This works magically for the __debug__ builtin, and `utils.BITCOIN_ONLY` is replaced
# by a literal True/False by us in the build step.
#
# Therefore, each of the following needs to include the respective static expression
# so that it can be correctly excluded from the resulting build.

if __debug__ and ENABLE_IFACE_DEBUG:
    # interface used for debug messages with trezor wire protocol
    id_debug = next(_iface_iter)
    iface_debug = io.WebUSB(
        iface_num=id_debug,
        ep_in=0x81 + id_debug,
        ep_out=0x01 + id_debug,
        emu_port=UDP_PORT + DEBUGLINK_PORT_OFFSET,
    )
    bus.add(iface_debug)
    active_iface.append(iface_debug)

if not utils.BITCOIN_ONLY and ENABLE_IFACE_WEBAUTHN:
    # interface used for FIDO/U2F and FIDO2/WebAuthn HID transport
    id_webauthn = next(_iface_iter)
    iface_webauthn = io.HID(
        iface_num=id_webauthn,
        ep_in=0x81 + id_webauthn,
        ep_out=0x01 + id_webauthn,
        emu_port=UDP_PORT + WEBAUTHN_PORT_OFFSET,
        # fmt: off
        report_desc=bytes([
            0x06, 0xd0, 0xf1,  # USAGE_PAGE (FIDO Alliance)
            0x09, 0x01,        # USAGE (U2F HID Authenticator Device)
            0xa1, 0x01,        # COLLECTION (Application)
            0x09, 0x20,        # USAGE (Input Report Data)
            0x15, 0x00,        # LOGICAL_MINIMUM (0)
            0x26, 0xff, 0x00,  # LOGICAL_MAXIMUM (255)
            0x75, 0x08,        # REPORT_SIZE (8)
            0x95, 0x40,        # REPORT_COUNT (64)
            0x81, 0x02,        # INPUT (Data,Var,Abs)
            0x09, 0x21,        # USAGE (Output Report Data)
            0x15, 0x00,        # LOGICAL_MINIMUM (0)
            0x26, 0xff, 0x00,  # LOGICAL_MAXIMUM (255)
            0x75, 0x08,        # REPORT_SIZE (8)
            0x95, 0x40,        # REPORT_COUNT (64)
            0x91, 0x02,        # OUTPUT (Data,Var,Abs)
            0xc0,              # END_COLLECTION
        ]),
        # fmt: on
    )
    bus.add(iface_webauthn)
    active_iface.append(iface_webauthn)

if __debug__ and ENABLE_IFACE_VCP:
    # interface used for cdc/vcp console emulation (debug messages)
    id_vcp = next(_iface_iter)
    id_vcp_data = next(_iface_iter)
    iface_vcp = io.VCP(
        iface_num=id_vcp,
        data_iface_num=id_vcp_data,
        ep_in=0x81 + id_vcp,
        ep_out=0x01 + id_vcp,
        ep_cmd=0x81 + id_vcp_data,
        emu_port=UDP_PORT + VCP_PORT_OFFSET,
    )
    bus.add(iface_vcp)
    active_iface.append(iface_vcp)
