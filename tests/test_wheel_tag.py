r"""Test wheel tag."""
from xmake_python.builder.wheel_tag import WheelTag


class Test:
    r"""Test."""

    @staticmethod
    def test_WheelTag() -> None:
        assert WheelTag.compute_best([]) != ""
