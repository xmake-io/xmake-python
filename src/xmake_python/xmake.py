from dataclasses import dataclass
from subprocess import run
from pathlib import Path
from shlex import split


@dataclass
class XMaker:
    xmake: str = "xmake"
    command: str = ""
    tempname: str = ""
    project: str = ""

    def config(self):
        text = ""
        # src/xmake_python/templates/xmake.lua
        with open(Path(__file__).parent / "templates" / "xmake.lua") as f:
            text = f.read()
        text = text.format(project=self.project, root=self.tempname)
        with open(Path(self.tempname) / "xmake.lua", "w") as f:
            f.write(text)
        cmd = [
            self.xmake,
            "config",
            "-yP",
            self.tempname,
        ] + split(self.command)
        run(cmd)

    def build(self):
        cmd = [self.xmake, "-yP", self.tempname, "--verbose"]
        run(cmd)

    def install(self):
        cmd = [self.xmake, "install", "-yP", self.tempname, "-o", self.tempname]
        run(cmd)
