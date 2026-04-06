#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK
import logging
import os
import struct
import pytest
from read_polys import make_polysdata, write_polys

logging.basicConfig(
    filename=f".{os.path.splitext(os.path.basename(__file__))[0]}.log",
    filemode="w",
    format="%(asctime)s %(name), %(message)s",
    datefmt="%H:%M:%S",
    level=logging.DEBUG,
)
logger = logging.getLogger(name=__name__)


class Descriptor:
    def __init__(self, format: str, offset: int):
        self._name = None
        self._format = format
        try:
            self._struct = struct.Struct(format)
        except struct.error:
            logger.error(f"{format}: bad format specifier")
        self._offset = offset

    def __set_name__(self, owner, name):
        self._name = name

    def __get__(self, instance, owner=None):
        if self is None:
            return self
        return self._struct.unpack_from(instance._buffer, self._offset)


class PolyMeta(type):
    def __new__(mcls, clsname, bases, clsdict):
        annotations = clsdict.get("__annotations__")
        offset = 0
        d = dict(clsdict)
        for attr, fmt in annotations.items():
            if not isinstance(fmt, str):
                raise ValueError(f"{fmt}: annotation must be str")
            descriptor = Descriptor(fmt, offset)
            descriptor.__set_name__(None, attr)
            d[attr] = descriptor
            if fmt == "<i":
                offset += 4
            elif fmt == "<d":
                offset += 8

        return super().__new__(mcls, clsname, bases, d)


class Structure:
    def __init__(self, bytedata):
        self._buffer = memoryview(bytedata)


class PolyHeader(Structure, metaclass=PolyMeta):
    code: "<i"  # noqa: F722
    minx: "<d"  # noqa: F722
    miny: "<d"  # noqa: F722
    maxx: "<d"  # noqa: F722
    maxy: "<d"  # noqa: F722
    npolys: "<i"  # noqa: F722


# class PolyHeader(Structure):
#     code = Descriptor("<i", 0)
#     minx = Descriptor("<d", 4)
#     miny = Descriptor("<d", 12)
#     maxx = Descriptor("<d", 20)
#     maxy = Descriptor("<d", 28)
#     npolys = Descriptor("<i", 36)


@pytest.fixture
def polysdata():
    return make_polysdata()


def test_polymeta(tmp_path, polysdata):
    polysbin = tmp_path / "polys.bin"
    write_polys(polysbin, polysdata)
    with open(polysbin, "rb") as f:
        buffer = f.read()
        polyheader = PolyHeader(buffer)
    for attr, res in zip(
        ["code", "minx", "miny", "maxx", "maxy", "npolys"],
        [
            (4660,),
            (12.34,),
            (90.12,),
            (12.34,),
            (89.01,),
            (3,),
        ],
    ):
        assert getattr(polyheader, attr) == res
    assert polysbin.exists()


# def test_polyheader(tmp_path, polysdata):
#     polysbin = tmp_path / "polys.bin"
#     write_polys(polysbin, polysdata)
#     with open(polysbin, "rb") as f:
#         buffer = f.read()
#         polyheader = PolyHeader(buffer)
#     for attr, res in zip(
#         ["code", "minx", "miny", "maxx", "maxy", "npolys"],
#         [
#             (4660,),
#             (12.34,),
#             (90.12,),
#             (12.34,),
#             (89.01,),
#             (3,),
#         ],
#     ):
#         assert getattr(polyheader, attr) == res
#     assert polysbin.exists()


# if __name__ == "__main__":
#     polysdat = make_polysdata()
#     write_polys("polys.bin", polysdat)
#     with open("polys.bin", "rb") as f:
#         buffer = f.read()
#         polyheader = PolyHeader(buffer)
#     print(polyheader.code)
#     print(polyheader.minx)
#     print(polyheader.miny)
#     print(polyheader.maxx)
#     print(polyheader.maxy)
#     print(polyheader.npolys)
