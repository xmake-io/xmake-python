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
)
from ..wheel import WheelBuilder

if TYPE_CHECKING:
    from collections.abc import Generator, Mapping

    from typing import Self

__all__ = ["GetRequires"]


def __dir__() -> list[str]:
    return __all__


def _load_scikit_build_settings(
    config_settings: Mapping[str, list[str] | str] | None = None,
) -> WheelBuilder:
    return WheelBuilder.from_ini_path(Path("pyproject.toml"), None)


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

    def xmake(self) -> Generator[str, None, None]:
        if self.settings.xmake is None:
            return
        if os.environ.get("XMAKE_EXECUTABLE", ""):
            return

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

    def dynamic_metadata(self) -> Generator[str, None, None]:
        for build_require in self.settings.metadata.build.requires:
            yield build_require.format(
                **pyproject_format(
                    settings=self.settings,
                )
            )
