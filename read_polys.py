#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK
from struct import Struct, calcsize
from dataclasses import dataclass
from itertools import chain

PolyType = list[tuple[float]]
PolysType = list[PolyType]
polys: PolysType = [
    [(12.34, 56.78), (90.12, 34.56), (78.90, 12.34)],
    [(45.67, 89.01), (23.45, 67.89), (12.34, 56.78), (90.12, 34.56)],
    [(78.90, 12.34), (45.67, 89.01), (23.45, 67.89)],
]


@dataclass
class PolysData:
    code: int
    min_x: float
    min_y: float
    max_x: float
    max_y: float
    polys: PolyType


def make_polysdata(polys: PolysType) -> PolysData:
    polysdata = PolysData()
    flatten = list(chain(*polys))
    polysdata.code = 0x1234
    polysdata.min_x = min(x for x, y in flatten)
    polysdata.max_x = max(x for x, y in flatten)
    polysdata.min_y = min(y for x, y in flatten)
    polysdata.max_y = max(y for x, y in flatten)
    polysdata.polys = polys
    return polysdata


def write_polys(filename: str, polysdata: PolysData) -> None:
    with open(filename, "wb") as f:

        def fwrite(data, format):
            s = Struct(format)
            f.write(s.pack(data))

        fwrite(polysdata.code, "<i")
        for dat in (polysdata.min_x, polysdata.min_y, polysdata.max_x, polysdata.max_y):
            fwrite(dat, "<d")
        fwrite(len(polysdata.polys), "<i")

        def write_poly(poly):
            fwrite(len(poly), "<i")
            for tup in poly:
                fwrite(tup, "<dd")

        for poly in polys:
            write_poly(poly)


def read_polys(filename: str) -> PolysData:
    polysdata = PolysData()
    with open(filename, "rb") as f:

        def fread(format):
            s = Struct(format)
            return s.unpack(f.read(s.size), format)

        polysdata.code = fread("<i")  # 0x1234
        polysdata.min_x = fread("<d")
        polysdata.min_y = fread("<d")
        polysdata.max_x = fread("<d")
        polysdata.max_y = fread("<d")

        npolys = fread("<i")

        def read_poly() -> PolyType:
            len = fread("<i")
            return [fread("<dd") for _ in range(len)]

        polysdata = [read_poly() for _ in range(npolys)]
        return polysdata
