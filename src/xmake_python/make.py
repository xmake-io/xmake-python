import os
from dataclasses import dataclass
from pathlib import Path
from shlex import join, split
from subprocess import run

from ._logging import rich_print
from .builder.wheel_tag import WheelTag


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
        self.configure = os.path.join(self.project, "configure.gnu")
        if not os.path.isfile(self.configure):
            self.configure = os.path.join(self.project, "configure")

    def run(self, commands, cwd=None):
        if cwd is None:
            cwd = self.cwd
        eol = "\n"
        if os.name == "nt":
            eol = "\r" + eol
        rich_print(
            f"{{bold}}$ cd {cwd}{eol}$ " + join(commands), color="green"
        )
        run(commands, cwd=cwd, check=True)

    def init(self):
        text = ""
        # src/make_python/templates/Makefile
        with open(Path(__file__).parent / "templates" / "Makefile") as f:
            text = f.read()
        if os.path.isfile(
            os.path.join(self.project, "configure.ac")
        ) and not os.path.isfile(os.path.join(self.project, "configure")):
            cmd = ["perl", "autoreconf", "-vif"]
            self.run(cmd, cwd=self.project)
        if os.path.isfile(self.configure):
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
        if os.path.isfile(self.configure):
            self.config(wheeltag)
        self.build()

    def config(self, wheeltag: WheelTag):
        cmd = [
            "sh",
            self.configure,
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

    def show(self):
        makefile = "Makefile.am"
        if os.path.exists(self.makefile):
            makefile = self.makefile
        if not os.path.exists(self.makefile):
            return 1
        with open(makefile) as f:
            text = f.read()
        if text.find(".c") == -1 and text.find(".h") == -1:
            return 0
        if text.find("pkg-config --cflags python") == -1:
            return 1
        return 2
