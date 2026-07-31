from __future__ import annotations

import subprocess
import sys

import pyperclip


class ClipboardError(RuntimeError):
    pass


def copy(text: str) -> None:
    try:
        pyperclip.copy(text)
    except pyperclip.PyperclipException as e:
        raise ClipboardError(
            "no clipboard mechanism found. On Linux install xclip or xsel; "
            "on macOS/Windows this should work out of the box."
        ) from e


def copy_with_autoclear(text: str, timeout: float) -> None:
    copy(text)
    if timeout <= 0:
        return

    kwargs = {}
    if sys.platform == "win32":
        kwargs["creationflags"] = (
            subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
        )
    else:
        kwargs["start_new_session"] = True

    proc = subprocess.Popen(
        [sys.executable, "-m", "password_generator.clipboard_clear", str(timeout)],
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        **kwargs,
    )
    proc.stdin.write(text.encode("utf-8"))
    proc.stdin.close()