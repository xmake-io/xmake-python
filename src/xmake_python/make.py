import os

from pathlib import Path
from dataclasses import dataclass
from subprocess import run, check_output, CalledProcessError
from shlex import split, join

from .builder.wheel_tag import WheelTag


@dataclass
class Maker:
    make: str = "make"
    command: str = ""
    tempname: str = ""
    project: str = ""
    version: str = ""
    makefile: str = ""

    def run(self, commands, cwd=None):
        if cwd is None:
            cwd = self.project
        print(join(commands))
        run(commands, cwd=cwd)

    def init(self):
        text = ""
        # src/make_python/templates/Makefile
        with open(Path(__file__).parent / "templates" / "Makefile") as f:
            text = f.read()
        if os.path.isfile(os.path.join(self.project, "configure")):
            self.project = os.path.join(self.tempname, "build")
        text = text.format(
            project=self.project.replace("\\", "\\\\"),
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
        cmd = [os.path.join(self.project, "configure"), "--prefix=/"] + split(
            self.command
        )
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
        return 0
