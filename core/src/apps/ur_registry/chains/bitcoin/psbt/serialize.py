import ustruct as struct
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List, Protocol, TypeVar, Callable, Sequence

    class Readable(Protocol):
        def read(self, length: int | None = -1) -> bytes:
            ...

    class Deserializable(Protocol):
        def deserialize(self, f: Readable) -> None:
            ...

    class Serializable(Protocol):
        def serialize(self) -> bytes:
            ...

    D = TypeVar("D", bound=Deserializable)


# Serialization/deserialization tools
def ser_compact_size(size: int) -> bytes:
    """
    Serialize an integer using Bitcoin's compact size unsigned integer serialization.

    :param size: The int to serialize
    :returns: The int serialized as a compact size unsigned integer
    """
    r = b""
    if size < 253:
        r = struct.pack("B", size)
    elif size < 0x10000:
        r = struct.pack("<BH", 253, size)
    elif size < 0x100000000:
        r = struct.pack("<BI", 254, size)
    else:
        r = struct.pack("<BQ", 255, size)
    return r


def deser_compact_size(s: Readable) -> int:
    """
    Deserialize a compact size unsigned integer from the beginning of the byte stream.

    :param s: The byte stream
    :returns: The integer that was serialized
    """
    nit: int = struct.unpack("<B", s.read(1))[0]
    if nit == 253:
        nit = struct.unpack("<H", s.read(2))[0]
    elif nit == 254:
        nit = struct.unpack("<I", s.read(4))[0]
    elif nit == 255:
        nit = struct.unpack("<Q", s.read(8))[0]
    return nit


def deser_string(s: Readable) -> bytes:
    """
    Deserialize a variable length byte string serialized with Bitcoin's variable length string serialization from a byte stream.

    :param s: The byte stream
    :returns: The byte string that was serialized
    """
    nit = deser_compact_size(s)
    return s.read(nit)


def ser_string(s: bytes) -> bytes:
    """
    Serialize a byte string with Bitcoin's variable length string serialization.

    :param s: The byte string to be serialized
    :returns: The serialized byte string
    """
    return ser_compact_size(len(s)) + s


def deser_uint256(s: Readable) -> int:
    """
    Deserialize a 256 bit integer serialized with Bitcoin's 256 bit integer serialization from a byte stream.

    :param s: The byte stream.
    :returns: The integer that was serialized
    """
    r = 0
    for i in range(8):
        t = struct.unpack("<I", s.read(4))[0]
        r += t << (i * 32)
    return r


def ser_uint256(u: int) -> bytes:
    """
    Serialize a 256 bit integer with Bitcoin's 256 bit integer serialization.

    :param u: The integer to serialize
    :returns: The serialized 256 bit integer
    """
    rs = b""
    for _ in range(8):
        rs += struct.pack("<I", u & 0xFFFFFFFF)
        u >>= 32
    return rs


def uint256_from_str(s: bytes) -> int:
    """
    Deserialize a 256 bit integer serialized with Bitcoin's 256 bit integer serialization from a byte string.

    :param s: The byte string
    :returns: The integer that was serialized
    """
    r = 0
    t = struct.unpack("<IIIIIIII", s[:32])
    for i in range(8):
        r += t[i] << (i * 32)
    return r


def deser_vector(s: Readable, c: Callable[[], D]) -> List[D]:
    """
    Deserialize a vector of objects with Bitcoin's object vector serialization from a byte stream.

    :param s: The byte stream
    :param c: The class of object to deserialize for each object in the vector
    :returns: A list of objects that were serialized
    """
    nit = deser_compact_size(s)
    r = []
    for _ in range(nit):
        t = c()
        t.deserialize(s)
        r.append(t)
    return r


def ser_vector(v: Sequence[Serializable]) -> bytes:
    """
    Serialize a vector of objects with Bitcoin's object vector serialzation.

    :param v: The list of objects to serialize
    :returns: The serialized objects
    """
    r = ser_compact_size(len(v))
    for i in v:
        r += i.serialize()
    return r


def deser_string_vector(s: Readable) -> List[bytes]:
    """
    Deserialize a vector of byte strings from a byte stream.

    :param f: The byte stream
    :returns: The list of byte strings that were serialized
    """
    nit = deser_compact_size(s)
    r = []
    for _ in range(nit):
        t = deser_string(s)
        r.append(t)
    return r


def ser_string_vector(v: List[bytes]) -> bytes:
    """
    Serialize a list of byte strings as a vector of byte strings.

    :param v: The list of byte strings to serialize
    :returns: The serialized list of byte strings
    """
    r = ser_compact_size(len(v))
    for sv in v:
        r += ser_string(sv)
    return r


def ser_sig_der(r: bytes, s: bytes) -> bytes:
    """
    Serialize the ``r`` and ``s`` values of an ECDSA signature using DER.

    :param r: The ``r`` value bytes
    :param s: The ``s`` value bytes
    :returns: The DER encoded signature
    """
    sig = b"\x30"

    # Make r and s as short as possible
    ri = 0
    for b in r:
        if b == 0:
            ri += 1
        else:
            break
    r = r[ri:]
    si = 0
    for b in s:
        if b == 0:
            si += 1
        else:
            break
    s = s[si:]

    # Make positive of neg
    first = r[0]
    if first & (1 << 7) != 0:
        r = b"\x00" + r
    first = s[0]
    if first & (1 << 7) != 0:
        s = b"\x00" + s

    # Write total length
    total_len = len(r) + len(s) + 4
    sig += struct.pack("B", total_len)

    # write r
    sig += b"\x02"
    sig += struct.pack("B", len(r))
    sig += r

    # write s
    sig += b"\x02"
    sig += struct.pack("B", len(s))
    sig += s

    sig += b"\x01"
    return sig


def ser_sig_compact(r: bytes, s: bytes, recid: bytes) -> bytes:
    """
    Serialize the ``r`` and ``s`` values of an ECDSA signature using the compact signature serialization scheme.

    :param r: The ``r`` value bytes
    :param s: The ``s`` value bytes
    :returns: The compact signature
    """
    rec = struct.unpack("B", recid)[0]
    prefix = struct.pack("B", 27 + 4 + rec)

    sig = b""
    sig += prefix
    sig += r + s

    return sig
