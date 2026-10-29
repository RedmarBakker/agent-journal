#!/usr/bin/env python3
"""Fail-closed event fallback while the staged bridge service is stopped."""

import json
import sys


def main() -> None:
    sys.stdin.readline()
    print(json.dumps({"v": 1}, separators=(",", ":")))


if __name__ == "__main__":
    main()
