from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Literal, NamedTuple

from packaging.version import InvalidVersion, Version

from ._logging import logger, rich_print
from ._shutil import Run

if TYPE_CHECKING:
    from collections.abc import Generator, Iterable

    from packaging.specifiers import SpecifierSet


__all__ = [
    "Program",
    "best_program",
    "get_xmake_program",
    "get_xmake_programs",
]


def __dir__() -> list[str]:
    return __all__


# Make sure we don't wait forever for programs to respond
# CI services can be really slow under load
if os.environ.get("CI", ""):
    TIMEOUT = 20
else:
    TIMEOUT = 10 if sys.platform.startswith("win") else 5


class Program(NamedTuple):
    path: Path
    version: Version | None


def _get_xmake_path(*, module: bool = True) -> Generator[Path, None, None]:
    """
    Get the path to xmake.
    """
    candidates = ("xmake",)
    for candidate in candidates:
        xmake_path = shutil.which(candidate)
        if xmake_path is not None:
            yield Path(xmake_path)


def get_xmake_program(xmake_path: Path) -> Program:
    """
    Get the Program (with version) for xmake given a path. The version will be
    None if it cannot be determined.

    `<https://github.com/xmake-io/xmake/discussions/6473>_`
    """
    try:
        result = Run(timeout=TIMEOUT).capture(xmake_path, "l", "xmake.version")
        try:
            v, _, d = result.stdout.partition("+")
            version = Version(
                v.split("m")[-1] + _ + d.split("\x1b")[0]
            )
            logger.info("xmake version via --version: {}", version)
            return Program(xmake_path, version)
        except (IndexError, InvalidVersion):
            logger.warning(
                "Could not determine xmake version via --version, got {!r}",
                result.stdout,
            )
    except subprocess.CalledProcessError as err:
        logger.warning(
            "Could not determine xmake version via --version, got {!r} {!r}",
            err.stdout,
            err.stderr,
        )
    except PermissionError:
        logger.warning("Permissions Error getting xmake's version")
    except subprocess.TimeoutExpired:
        logger.warning("Accessing xmake timed out, ignoring")

    return Program(xmake_path, None)


def get_xmake_programs(*, module: bool = True) -> Generator[Program, None, None]:
    """
    Get the path and version for xmake. If the version cannot be determined,
    yiels (path, None). Otherwise, yields (path, version). Best matches are
    yielded first.
    """
    for xmake_path in _get_xmake_path(module=module):
        yield get_xmake_program(xmake_path)


def _get_make_path(*, module: bool = True) -> Generator[Path, None, None]:
    """
    Get the path to make.
    """
    candidates = ("make",)
    for candidate in candidates:
        make_path = shutil.which(candidate)
        if make_path is not None:
            yield Path(make_path)


def get_make_program(make_path: Path) -> Program:
    """
    Get the Program (with version) for make given a path. The version will be
    None if it cannot be determined.
    """
    try:
        result = Run(timeout=TIMEOUT).capture(make_path, "--version")
        try:
            version = Version(result.stdout.split()[2])
            logger.info("make version via --version: {}", version)
            return Program(make_path, version)
        except (IndexError, InvalidVersion):
            logger.warning(
                "Could not determine make version via --version, got {!r}",
                result.stdout,
            )
    except subprocess.CalledProcessError as err:
        logger.warning(
            "Could not determine make version via --version, got {!r} {!r}",
            err.stdout,
            err.stderr,
        )
    except PermissionError:
        logger.warning("Permissions Error getting make's version")
    except subprocess.TimeoutExpired:
        logger.warning("Accessing make timed out, ignoring")

    return Program(make_path, None)


def get_make_programs(*, module: bool = True) -> Generator[Program, None, None]:
    """
    Get the path and version for make. If the version cannot be determined,
    yiels (path, None). Otherwise, yields (path, version). Best matches are
    yielded first.
    """
    for make_path in _get_make_path(module=module):
        yield get_make_program(make_path)


def _get_autoreconf_path(*, module: bool = True) -> Generator[Path, None, None]:
    """
    Get the path to autoreconf.
    """
    candidates = ("autoreconf",)
    for candidate in candidates:
        autoreconf_path = shutil.which(candidate)
        if autoreconf_path is not None:
            yield Path(autoreconf_path)


def get_autoreconf_program(autoreconf_path: Path) -> Program:
    """
    Get the Program (with version) for autoreconf given a path. The version will be
    None if it cannot be determined.
    """
    try:
        result = Run(timeout=TIMEOUT).capture(autoreconf_path, "--version")
        try:
            version = Version(result.stdout.split()[3])
            logger.info("autoreconf version via --version: {}", version)
            return Program(autoreconf_path, version)
        except (IndexError, InvalidVersion):
            logger.warning(
                "Could not determine autoreconf version via --version, got {!r}",
                result.stdout,
            )
    except subprocess.CalledProcessError as err:
        logger.warning(
            "Could not determine autoreconf version via --version, got {!r} {!r}",
            err.stdout,
            err.stderr,
        )
    except PermissionError:
        logger.warning("Permissions Error getting autoreconf's version")
    except subprocess.TimeoutExpired:
        logger.warning("Accessing autoreconf timed out, ignoring")

    return Program(autoreconf_path, None)


def get_autoreconf_programs(*, module: bool = True) -> Generator[Program, None, None]:
    """
    Get the path and version for autoreconf. If the version cannot be determined,
    yiels (path, None). Otherwise, yields (path, version). Best matches are
    yielded first.
    """
    for autoreconf_path in _get_autoreconf_path(module=module):
        yield get_autoreconf_program(autoreconf_path)


def best_program(
    programs: Iterable[Program], *, version: SpecifierSet | None
) -> Program | None:
    """
    Select the first program entry that is of a supported version, or None if not found.
    """

    for program in programs:
        if version is None:
            return program
        if program.version is not None and version.contains(program.version):
            return program

    return None


def info_print(
    *,
    color: Literal[
        "", "black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"
    ] = "",
) -> None:
    """
    Print information about the program search.
    """
    rich_print("{bold}Detected xmake (all versions):", color=color)
    for n, prog in enumerate(get_xmake_programs()):
        # s = " " if n else "{default}*{color}"
        s = " "
        rich_print(
            f"{s} {{bold}}xmake:{{normal}} {prog.path} {prog.version!r}", color=color
        )


if __name__ == "__main__":
    info_print()
