#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK
from typing import BinaryIO
from struct import Struct

RecordType = tuple[int, float, float]


def write_records(records: list[RecordType], format: str, f: BinaryIO):
    s = Struct(format)
    for r in records:
        f.write(s.pack(*r))


if __name__ == "__main__":
    records = [
        (1, 2.3, 4.5),
        (6, 7.8, 9.0),
        (12, 13.4, 56.7),
    ]
    with open("data.bin", "wb") as f:
        write_records(records, "<idd", f)
