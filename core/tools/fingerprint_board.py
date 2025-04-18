#!/usr/bin/env python
from __future__ import print_function

import binascii
import hashlib


def H(x):
    return hashlib.sha256(x).digest()


def compute_fingerprint(x, double):
    digest = H(H(x)) if double else H(x)
    return binascii.hexlify(digest).decode()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument("file", type=argparse.FileType("rb"),
                        help="input file")
    parser.add_argument("--offset", type=int, default=0,
                        help="skip bytes at start of input")
    parser.add_argument("--max-size", type=int,
                        help="maximum input file size")
    parser.add_argument("--double", action="store_true",
                        help="use SHA-256d instead of SHA-256")

    args = parser.parse_args()

    data = args.file.read()
    data = data[:-32] + b'\0' * 32
    size = len(data)
    fingerprint = compute_fingerprint(data[args.offset:], True)

    print("Filename    :", args.file.name)
    print("Fingerprint :", fingerprint)

    print(f"Size        : {size} bytes (out of {args.max_size} maximum)")
