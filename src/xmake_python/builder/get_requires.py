from __future__ import annotations

import dataclasses
import os
from typing import TYPE_CHECKING
from pathlib import Path

from .._logging import logger
from ..format import pyproject_format
from ..program_search import (
    best_program,
    get_xmake_programs,
    get_make_programs,
    get_autoreconf_programs,
)
from ..wheel import WheelBuilder, get_build_system
from ..config import read_xmake_config

if TYPE_CHECKING:
    from collections.abc import Generator, Mapping

    from typing import Self

__all__ = ["GetRequires"]


def __dir__() -> list[str]:
    return __all__


def _load_scikit_build_settings(
    config_settings: Mapping[str, list[str] | str] | None = None,
) -> WheelBuilder:
    ini_path = Path("pyproject.toml")
    return WheelBuilder.from_ini_path(ini_path, None)


@dataclasses.dataclass(frozen=True)
class GetRequires:
    settings: WheelBuilder = dataclasses.field(
        default_factory=_load_scikit_build_settings
    )

    @classmethod
    def from_config_settings(
        cls, config_settings: Mapping[str, list[str] | str] | None
    ) -> Self:
        return cls(_load_scikit_build_settings(config_settings))

    def get_build_system(self):
        ini_path = Path("pyproject.toml")
        directory = ini_path.parent
        ini_info = read_xmake_config(ini_path)
        maker = ini_info.dtool.get("maker", {})

        xmake_path = directory / "xmake.lua"
        configure_ac_path = directory / "configure.ac"
        configure_path = directory / "configure"
        make_path = directory / maker.get("makefile", "Makefile")
        build_system = get_build_system(xmake_path, make_path, configure_path, configure_ac_path)
        return build_system

    def get_requires(self) -> Generator[str, None, None]:
        if self.settings.xmake is None:
            return
        if os.environ.get("XMAKE_EXECUTABLE", "") or os.environ.get("MAKE_EXECUTABLE", ""):
            return
        build_system = self.get_build_system()
        if build_system == "xmake":
            xmake_verset = None
            # xmake_verset = self.settings.xmake.version
            #
            # # If the module is already installed (via caching the build
            # # environment, for example), we will use that
            # if importlib.util.find_spec("xmake") is not None:
            #     yield f"xmake{xmake_verset}"
            #     return

            xmake = best_program(
                get_xmake_programs(module=False), version=xmake_verset
            )
            if xmake is None:
                if xmake_verset is None:
                    yield "xmake-wheel"
                else:
                    yield f"xmake-wheel{xmake_verset}"
                return
            logger.debug(
                "Found system xmake: {} - not requiring PyPI package", xmake
            )
        elif build_system in ["make", "autotools"]:
            make_verset = None
            make = best_program(
                get_make_programs(module=False), version=make_verset
            )
            if make is None:
                if make_verset is None:
                    yield "make"
                else:
                    yield f"make{make_verset}"
                return
            logger.debug(
                "Found system make: {} - not requiring PyPI package", make
            )
        if build_system == "autotools":
            autotools_verset = None
            autotools = best_program(
                get_autoreconf_programs(module=False), version=autotools_verset
            )
            if autotools is None:
                if autotools_verset is None:
                    yield "gnuautoconf"
                else:
                    yield f"gnuautoconf{autotools_verset}"
                return
            logger.debug(
                "Found system autotools: {} - not requiring PyPI package", autotools
            )

    def dynamic_metadata(self) -> Generator[str, None, None]:
        for build_require in self.settings.metadata.build.requires:
            yield build_require.format(
                **pyproject_format(
                    settings=self.settings,
                )
            )
