import json

from dataclasses import dataclass
from subprocess import run, check_output, CalledProcessError
from pathlib import Path
from shlex import split


@dataclass
class XMaker:
    xmake: str = "xmake"
    command: str = ""
    tempname: str = ""
    project: str = ""
    version: str = ""

    def config(self):
        text = ""
        # src/xmake_python/templates/xmake.lua
        with open(Path(__file__).parent / "templates" / "xmake.lua") as f:
            text = f.read()
        text = text.format(project=self.project.replace("\\", "\\\\"), root=self.tempname.replace("\\", "\\\\"), version=self.version)
        with open(Path(self.tempname) / "xmake.lua", "w") as f:
            f.write(text)
        cmd = [
            self.xmake,
            "config",
            "-y",
            "-P",
            self.tempname,
        ] + split(self.command)
        run(cmd)

    def build(self):
        cmd = [self.xmake, "-y", "-P", self.tempname, "--verbose"]
        run(cmd)

    def install(self):
        cmd = [self.xmake, "install", "-y", "-P", self.tempname, "-o", self.tempname]
        run(cmd)

    @staticmethod
    def check_output(cmd: list[str]):
        b = b""
        try:
            b = check_output(cmd)
        except CalledProcessError as e:
            b: bytes = e.stdout
        return b.decode()

    def show(self):
        cmd = [self.xmake, "show", "-y", "-P", self.tempname, "-ltargets", "--json"]
        targets = json.loads(self.check_output(cmd))
        kinds = []
        for target in targets:
            kind = 0
            cmd = [self.xmake, "show", "-y", "-P", self.tempname, "-t", target]
            text = self.check_output(cmd)
            if text.find("phony") == -1 or text.find("packages") != -1:
                kind = 1
                if text.find("python.") != -1:
                    kind = 2
            kinds += [kind]
        if 2 in kinds:
            return 2
        if 1 in kinds:
            return 1
        return 0
