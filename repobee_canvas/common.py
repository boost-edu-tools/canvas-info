"""Logging functions for the canvas plugin commands.

Functions:
- inform: Show an informational message.
- warn: Show a warning.
- fault: Show an error message.
"""
from pathlib            import Path
import re
import sys

def warn(msg : str, error : BaseException = None) -> None:
    """Warn the user."""
    print(f"WARNING: {msg}")
    if error:
        print(f"\t{str(error)}")

def fault(msg : str, error : BaseException = None) -> None:
    """Warn the user about a fault in using repobee-canvas."""
    print(f"ERROR: {msg}")
    if error:
        print(f"\t{str(error)}")

def inform(msg : str, spacing : int = 0) -> None:
    """Inform the user."""
    print(msg)

    if spacing > 0:
        vspace(spacing - 1)

def vspace(size : int = 0)  -> None:
    """Add a vertical space of size lines."""
    print("\n" * size)

def ask_password(question : str) -> str:
    """Ask for a password"""
    return Password(
            prompt = question,
            hidden = "*",
            ).launch()

def ask_open(question : str, default : str = None) -> str:
    """Ask the user an open question."""
    return Input(
            prompt = question,
            strip = True,
            default = "" if default is None else default
           ).launch()

def ask_closed(question : str) -> str:
    """Ask the user an closed question."""
    return YesNo(prompt = question).launch()

def ask_continue(question : str, exit_msg : str = "Command init-course stopped."):
    """Ask the user if she wants to continue or stop."""
    if not YesNo(prompt = question).launch():
        inform(exit_msg)
        sys.exit()

def ask_dir(question : str, suggestion : str = "") -> str:
    """Ask for a directory and check it does not yet exist."""
    dir_name = ask_open(question, suggestion)

    if not dir_name and suggestion:
        dir_name = suggestion

    if Path(dir_name).exists():
        warn(f"Directory {dir_name} already exists.")
        ask_continue("Do you want to continue and enter another directory?")
        return ask_dir(question)

    return dir_name

def str_to_path(string_path : str) -> str:
    """Convert a string to a string suitable as a path."""
    path = re.sub(r"\s+", "_", string_path)
    path = re.sub(r"[^\w]", "", path)
    return path
