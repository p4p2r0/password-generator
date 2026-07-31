from __future__ import annotations

import sys
import time

import pyperclip


def main() -> None:
    timeout = float(sys.argv[1])
    secret = sys.stdin.buffer.read().decode("utf-8")
    time.sleep(timeout)
    if pyperclip.paste() == secret:
        pyperclip.copy("")


if __name__ == "__main__":
    main()