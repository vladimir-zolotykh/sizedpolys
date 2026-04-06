#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK
from struct import Struct


class Descriptor:
    def __init__(self, format: str, offset: int):
        self._name = None
        self._format = format
        self._struct = Struct(format)
        self._offset = offset

    def __set_name__(self, owner, name):
        self._name = name

    def __get__(self, instance, owner=None):
        if self is None:
            return self
        return self._struct.unpack_from(instance._buffer, self._offset)


class Structure:
    def __init__(self, bytedata):
        self._buffer = memoryview(bytedata)


class PolyHeader(Structure):
    code = Descriptor("<i", 0)
    minx = Descriptor("<d", 4)
    miny = Descriptor("<d", 12)
    maxx = Descriptor("<d", 20)
    maxy = Descriptor("<d", 28)
    npolys = Descriptor("<i", 36)


def test_polyheader():
    from read_polys import make_polysdata, write_polys

    polysdata = make_polysdata()
    write_polys("polys.bin", polysdata)
    with open("polys.bin", "rb") as f:
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


if __name__ == "__main__":
    from read_polys import make_polysdata, write_polys

    polysdata = make_polysdata()
    write_polys("polys.bin", polysdata)
    with open("polys.bin", "rb") as f:
        buffer = f.read()
        polyheader = PolyHeader(buffer)
    print(polyheader.code)
    print(polyheader.minx)
    print(polyheader.miny)
    print(polyheader.maxx)
    print(polyheader.maxy)
    print(polyheader.npolys)
