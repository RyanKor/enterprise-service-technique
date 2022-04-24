from __future__ import division
from struct import pack, unpack
from typing import List, TextIO


def encode_number(number: int) -> TextIO:
    """
    VB Code Encode Number method
    :param number:
    :return:
    Usage
        import vb
        vb.encode_number(128)
    """
    byte_lists = []
    while True:
        byte_lists.insert(0, number % 128)
        if number < 128:
            break
        number = number // 128
    byte_lists[-1] += 128
    return pack("%dB" % len(byte_lists), *byte_lists)


def encode(number: List[int]) -> TextIO:
    """
    VB Code Encode method
    :param number:
    :return:
    Usage
        import vb
        vb.encode([32, 64, 128])
    """
    return b"".join([encode_number(num) for num in number])


def decode(bytestream: TextIO) -> List[int]:
    """
    VB Code Decode method
    :param bytestream:
    :return:
    Usage
        import vb
        vb.decode(b'\xa0\xc0\x01\x80') # bytestream type
    """
    n = 0
    numbers = []
    bytestream = unpack('%dB' % len(bytestream), bytestream)
    for byte in bytestream:
        if byte < 128:
            n = 128 * n + byte
        else:
            n = 128 * n + (byte - 128)
            numbers.append(n)
            n = 0
    return numbers

if __name__=='__main__':
    numbers = (1,2,128,145)
    res = encode(numbers)
    print(decode(res))