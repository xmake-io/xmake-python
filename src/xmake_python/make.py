import os

from pathlib import Path
from dataclasses import dataclass
from subprocess import run, check_output, CalledProcessError
from shlex import split, join

from .builder.wheel_tag import WheelTag
from ._logging import rich_print


@dataclass
class Maker:
    make: str = "make"
    command: str = ""
    tempname: str = ""
    project: str = ""
    version: str = ""
    makefile: str = ""

    def __post_init__(self):
        self.cwd = self.project

    def run(self, commands, cwd=None):
        if cwd is None:
            cwd = self.cwd
        rich_print(f"{{bold}}$ cd {cwd}\n$ " + join(commands), color="green")
        run(commands, cwd=cwd)

    def init(self):
        text = ""
        # src/make_python/templates/Makefile
        with open(Path(__file__).parent / "templates" / "Makefile") as f:
            text = f.read()
        if os.path.isfile(os.path.join(self.project, "configure.ac")):
            cmd = ["autoreconf", "-vif"]
            self.run(cmd, cwd=self.project)
        if os.path.isfile(os.path.join(self.project, "configure")):
            self.cwd = os.path.join(self.tempname, "build")
            os.mkdir(self.cwd)
        text = text.format(
            project=self.cwd.replace("\\", "\\\\"),
            root=self.tempname.replace("\\", "\\\\"),
            version=self.version,
            makefile=self.makefile,
        )
        with open(Path(self.tempname) / "Makefile", "w") as f:
            f.write(text)

    def package(self, wheeltag: WheelTag):
        if os.path.isfile(os.path.join(self.project, "configure")):
            self.config(wheeltag)
        self.build()

    def config(self, wheeltag: WheelTag):
        cmd = [
            os.path.join(self.project, "configure"),
            "--prefix=" + os.path.join(self.tempname, "data"),
        ] + split(self.command)
        self.run(cmd, cwd=os.path.join(self.tempname, "build"))

    def build(self):
        cmd = [self.make, "-f", os.path.join(self.tempname, "Makefile")]
        self.run(cmd)

    def install(self):
        cmd = [
            self.make,
            "-f",
            os.path.join(self.tempname, "Makefile"),
            "install",
        ]
        self.run(cmd)

    def check_output(self, cmd: list[str]):
        b = b""
        try:
            b = check_output(cmd, cwd=self.tempname)
        except CalledProcessError as e:
            b: bytes = e.stdout
        return b.decode()

    def show(self):
        makefile = "Makefile.am"
        if os.path.exists(self.makefile):
            makefile = self.makefile
        with open(makefile) as f:
            text = f.read()
        if text.find(".c") == -1:
            return 0
        if text.find("pkg-config --cflags python") == -1:
            return 1
        return 2
