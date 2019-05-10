import ast
import base64
import binascii
import collections
import ctypes
import datetime
import functools
import glob
import hashlib
import io
import itertools
import json
import math
import operator
import os
import pickle
import platform
import random
import re
import shutil
import socket
import string
import struct
import subprocess
import sys
import textwrap
import time
import timeit
import webbrowser
from io import open

try:
    import urllib.parse
except ImportError:
    import urllib

try:
    import html
except ImportError:
    pass

try:
    import statistics
except ImportError:
    pass

try:
    import secrets
except ImportError:
    pass

try:
    import chardet
    import requests
except ImportError:
    pass

PY2 = sys.version_info[0] < 3


def _auto_encode(s):
    return s.encode() if not PY2 and isinstance(s, str) else s


def _auto_decode(s):
    return s if PY2 else s.decode()


def read(filename, encoding='utf-8'):
    with open(filename, 'r', encoding=encoding) as fin:
        return fin.read()


def readb(filename):
    with open(filename, 'rb') as fin:
        return fin.read()


def readlines(filename, encoding='utf-8', strip_newline=True):
    with open(filename, 'r', encoding=encoding) as fin:
        for line in fin:
            if strip_newline:
                yield line.rstrip('\n')
            else:
                yield line


def readjson(filename, encoding='utf-8', **kw):
    with open(filename, 'r', encoding=encoding) as fin:
        return json.load(fin, **kw)


def write(filename, content, encoding='utf-8'):
    with open(filename, 'w', encoding=encoding) as fout:
        fout.write(content)


def writeb(filename, content):
    with open(filename, 'wb') as fout:
        fout.write(content)


def writelines(filename, content, encoding='utf-8', append_newline=True):
    with open(filename, 'w', encoding=encoding) as fout:
        for line in content:
            fout.write(line)

            if append_newline:
                fout.write('\n')


def writejson(filename, content, encoding='utf-8', **kw):
    with open(filename, 'w', encoding=encoding) as fout:
        json.dump(content, fout, **kw)


def even_split(s, n):
    return [''.join(item) for item in zip(*([iter(s)] * n))]


def even_split_b(s, n):
    if PY2:
        return even_split(s, n)
    else:
        return [bytes(item) for item in zip(*([iter(s)] * n))]


_word_size_dict = {
    None: None,
    8: 'b',
    16: 'h',
    32: 'i',
    64: 'q'
}

_endian_dict = {
    None: sys.byteorder,
    '@': sys.byteorder,
    '=': sys.byteorder,
    '<': 'little',
    '>': 'big',
    '!': 'big',
    'little': 'little',
    'big': 'big'
}


def pack(x, word_size=None, endian=None, signed=False):
    if word_size not in _word_size_dict:
        raise ValueError('invalid word size')

    if endian not in _endian_dict:
        raise ValueError('invalid endian')

    word_size = _word_size_dict[word_size]
    endian = _endian_dict[endian]
    signed = bool(signed)

    if word_size is None:  # automatically determine byte length, only works in Python 3
        return x.to_bytes((x.bit_length() + 7) // 8, byteorder=endian, signed=signed) or b'\x00'
    else:
        if not signed:
            word_size = word_size.upper()

        endian = '<' if endian == 'little' else '>'
        return struct.pack(endian + word_size, x)


def unpack(s, word_size=None, endian=None, signed=False):
    if word_size not in _word_size_dict:
        raise ValueError('invalid word size')

    if endian not in _endian_dict:
        raise ValueError('invalid endian')

    word_size = _word_size_dict[word_size]
    endian = _endian_dict[endian]
    signed = bool(signed)

    if word_size is None:  # automatically determine byte length, only works in Python 3
        return int.from_bytes(s, byteorder=endian, signed=signed)
    else:
        if not signed:
            word_size = word_size.upper()

        endian = '<' if endian == 'little' else '>'
        return struct.unpack(endian + word_size, s)[0]


p8 = functools.partial(pack, word_size=8)
u8 = functools.partial(unpack, word_size=8)
p16 = functools.partial(pack, word_size=16)
u16 = functools.partial(unpack, word_size=16)
p32 = functools.partial(pack, word_size=32)
u32 = functools.partial(unpack, word_size=32)
p64 = functools.partial(pack, word_size=64)
u64 = functools.partial(unpack, word_size=64)


def i8(x):
    return ctypes.c_byte(x).value


def ui8(x):
    return ctypes.c_ubyte(x).value


def i16(x):
    return ctypes.c_short(x).value


def ui16(x):
    return ctypes.c_ushort(x).value


def i32(x):
    return ctypes.c_int(x).value


def ui32(x):
    return ctypes.c_uint(x).value


def i64(x):
    return ctypes.c_longlong(x).value


def ui64(x):
    return ctypes.c_ulonglong(x).value


def b16e(s):
    return _auto_decode(base64.b16encode(_auto_encode(s)))


def b32e(s):
    return _auto_decode(base64.b32encode(_auto_encode(s)))


def b64e(s):
    return _auto_decode(base64.b64encode(_auto_encode(s)))


if not PY2:
    def b85e(s):
        return _auto_decode(base64.b85encode(_auto_encode(s)))

b16d = base64.b16decode
b32d = base64.b32decode
b64d = base64.b64decode

if not PY2:
    b85d = base64.b85decode


def enhex(s):
    return _auto_decode(binascii.hexlify(_auto_encode(s)))


unhex = binascii.unhexlify

urlencode = urllib.quote if PY2 else urllib.parse.quote
urldecode = urllib.unquote_plus if PY2 else urllib.parse.unquote_plus


def i2b(x):
    return chr(x) if PY2 else bytes([x])


def xorb(s1, s2):
    if PY2:
        return ''.join(chr(ord(b1) ^ ord(b2)) for b1, b2 in zip(s1, s2))
    else:
        return bytes(b1 ^ b2 for b1, b2 in zip(s1, s2))


# From: https://gist.github.com/vqhuy/a7a5cde5ce1b679d3c0a
def rol(val, r_bits, max_bits):
    return (val << (r_bits % max_bits)) & (2 ** max_bits - 1) | \
           (val & (2 ** max_bits - 1)) >> (max_bits - r_bits % max_bits)


def ror(val, r_bits, max_bits):
    return (val & (2 ** max_bits - 1)) >> (r_bits % max_bits) | \
           (val << (max_bits - r_bits % max_bits)) & (2 ** max_bits - 1)


def md5(s):
    return hashlib.md5(_auto_encode(s)).hexdigest()


def md5_b(s):
    return hashlib.md5(_auto_encode(s)).digest()


def sha1(s):
    return hashlib.sha1(_auto_encode(s)).hexdigest()


def sha1_b(s):
    return hashlib.sha1(_auto_encode(s)).digest()


def sha256(s):
    return hashlib.sha256(_auto_encode(s)).hexdigest()


def sha256_b(s):
    return hashlib.sha256(_auto_encode(s)).digest()


def crc32(s):
    return hex(binascii.crc32(_auto_encode(s)) & 0xffffffff)[2:10]


def rgb2hex(r, g, b):
    if not isinstance(r, int):
        raise TypeError('r value should be an integer')

    if r < 0 or r > 255:
        raise ValueError('r value should be in [0, 255]')

    if not isinstance(g, int):
        raise TypeError('g value should be an integer')

    if g < 0 or g > 255:
        raise ValueError('g value should be in [0, 255]')

    if not isinstance(b, int):
        raise TypeError('b value should be an integer')

    if b < 0 or b > 255:
        raise ValueError('b value should be in [0, 255]')

    return '#%02x%02x%02x' % (r, g, b)


def hex2rgb(h):
    if not re.match(r'\A#?[0-9a-fA-F]{6}\Z', h):
        raise ValueError('invalid hex color')

    h = h.replace('#', '')
    return int(h[:2], 16), int(h[2:4], 16), int(h[4:], 16)


def pretty_number(x, precision=2):
    if not isinstance(x, (int, float)):
        raise TypeError('x should be a number')

    if not isinstance(precision, int):
        raise TypeError('precision should be an integer')

    if precision < 0:
        raise ValueError('precision should be non-negative')

    return str(int(x)) if int(x) == x else ('%.' + str(precision) + 'f') % x


def pretty_size(size):
    if not isinstance(size, int):
        raise TypeError('size should be an integer')

    if size < 0:
        raise ValueError('size should be non-negative')

    if size == 0:
        return '0B'

    units = ('B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'BB')
    order = min(int(math.log(size, 1024)), len(units) - 1)
    return pretty_number(float(size) / 1024 ** order) + units[order]


def pretty_time(t):
    return str(datetime.timedelta(seconds=t))


def curl(url, method='GET', **kw):
    r = requests.request(method, url, **kw)
    return r.text


def curlb(url, method='GET', **kw):
    r = requests.request(method, url, **kw)
    return r.content


if platform.system() != 'Windows':
    libc = ctypes.CDLL(None)
