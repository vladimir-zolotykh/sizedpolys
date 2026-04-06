#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK
from typing import get_origin, get_args, Annotated
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
        # return self._struct.unpack_from(instance._buffer, self._offset)
        t = self._struct.unpack_from(instance._buffer, self._offset)
        if len(t) == 1:
            return t[0]
        else:
            return t


class PolyMeta(type):
    def __new__(mcls, clsname, bases, clsdict):
        annotations = clsdict.get("__annotations__", {})
        offset = 0
        d = dict(clsdict)
        for attr, anno in annotations.items():
            if get_origin(anno) is Annotated:
                _, fmt = get_args(anno)
            else:
                raise TypeError("Expected Annotated[...]")
            descriptor = Descriptor(fmt, offset)
            descriptor.__set_name__(None, attr)
            d[attr] = descriptor
            if fmt == "<i":
                offset += 4
            elif fmt == "<d":
                offset += 8

        return super().__new__(mcls, clsname, bases, d)


class Structure(metaclass=PolyMeta):
    def __init__(self, bytedata):
        self._buffer = memoryview(bytedata)


class PolyHeader(Structure):
    code: Annotated[int, "<i"]
    minx: Annotated[float, "<d"]
    miny: Annotated[float, "<d"]
    maxx: Annotated[float, "<d"]
    maxy: Annotated[float, "<d"]
    npolys: Annotated[int, "<i"]


class Point(Structure):
    x: Annotated[int, "<d"]
    y: Annotated[int, "<d"]


def write_point(filename: str) -> None:
    with open(filename, "wb") as f:

        def fwrite(data, format):
            s = struct.Struct(format)
            if isinstance(data, tuple):
                f.write(s.pack(*data))
            else:
                f.write(s.pack(data))

        fwrite(10.1, "<d")
        fwrite(20.2, "<d")


def test_point(tmp_path):
    pointbin = tmp_path / "point.bin"
    write_point(pointbin)
    with open(pointbin, "rb") as f:
        buffer = f.read()
        point = Point(buffer)
    assert (point.x, point.y) == (10.1, 20.2)


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
            4660,
            12.34,
            90.12,
            12.34,
            89.01,
            3,
        ],
    ):
        assert getattr(polyheader, attr) == res
    assert polysbin.exists()
