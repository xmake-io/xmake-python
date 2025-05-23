from dataclasses import dataclass
from subprocess import run
from pathlib import Path
from shlex import split


@dataclass
class XMaker:
    xmake: str = "xmake"
    root: str = "."
    command: str = ""
    tempname: str = ""
    project: str = ""

    def config(self):
        text = ""
        # src/xmake_python/templates/xmake.lua
        with open(Path(__file__).parent / "templates" / "xmake.lua") as f:
            text = f.read()
        text = text.format(project=self.project)
        with open(Path(self.tempname) / "xmake.lua", "w") as f:
            f.write(text)
        run([self.xmake, "config", "-P", self.tempname] + split(self.command))

    def build(self):
        run([self.xmake, "-y", "-P", self.tempname, "--verbose"])

    def install(self):
        run([self.xmake, "install", "-P", self.tempname, "-o", self.tempname])
