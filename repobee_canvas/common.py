"""Logging functions for the canvas plugin commands.

Functions:
- inform: Show an informational message.
- warn: Show a warning.
- fault: Show an error message.
"""

import PySimpleGUI as sg

CLI = True


def cprint(msg: str, c=None) -> None:
    if CLI:
        print(msg)
    else:
        sg.cprint(msg, c=c)


def warn(msg: str, error: BaseException = None) -> None:
    """Warn the user."""
    cprint(f"WARNING: {msg}", c="white on red")
    if error:
        cprint(f"\t{str(error)}", c="white on red")


def fault(msg: str, error: BaseException = None) -> None:
    """Warn the user about a fault in using repobee-canvas."""
    cprint(f"ERROR: {msg}", c="white on red")
    if error:
        cprint(f"\t{str(error)}", c="white on red")


def inform(msg: str, spacing: int = 0) -> None:
    """Inform the user."""
    cprint(msg)

    if spacing > 0:
        vspace(spacing - 1)


def vspace(size: int = 0) -> None:
    """Add a vertical space of size lines."""
    cprint("\n" * size)
