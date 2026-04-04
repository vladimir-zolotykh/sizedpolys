#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK
from typing import BinaryIO
from struct import Struct, calcsize
from functools import partial

RecordType = tuple[int, float, float]


def write_records(records: list[RecordType], format: str, f: BinaryIO):
    s = Struct(format)
    for r in records:
        f.write(s.pack(*r))


def read_records(format: str, f: BinaryIO) -> list[RecordType]:
    s = Struct(format)
    size = calcsize(format)
    return [s.unpack(r) for r in iter(partial(f.read, size), b"")]


def test_write_records(tmp_path) -> None:
    records: list[RecordType] = [
        (1, 2.3, 4.5),
        (6, 7.8, 9.0),
        (12, 13.4, 56.7),
    ]
    fmt = "<idd"
    file_path = tmp_path / "data.bin"
    with open(file_path, "wb") as f:
        write_records(records, fmt, f)
    with open(file_path, "rb") as f:
        got_records = read_records(fmt, f)
    assert records == got_records
