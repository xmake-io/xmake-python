import json

from dataclasses import dataclass
from subprocess import run, check_output, CalledProcessError
from pathlib import Path
from shlex import split, join

from .builder.wheel_tag import WheelTag


@dataclass
class XMaker:
    xmake: str = "xmake"
    command: str = ""
    tempname: str = ""
    project: str = ""
    version: str = ""

    def init(self):
        text = ""
        # src/xmake_python/templates/xmake.lua
        with open(Path(__file__).parent / "templates" / "xmake.lua") as f:
            text = f.read()
        text = text.format(
            project=self.project.replace("\\", "\\\\"),
            root=self.tempname.replace("\\", "\\\\"),
            version=self.version,
        )
        with open(Path(self.tempname) / "xmake.lua", "w") as f:
            f.write(text)

    def run(self, commands):
        print(join(commands))
        run(commands, cwd=self.tempname)

    def package(self, wheeltag: WheelTag):
        commands = []
        if wheeltag.arch == "win32":
            commands = ["-a", "x86"]
        elif wheeltag.arch == "win_amd64":
            commands = ["-a", "x64"]
        elif wheeltag.arch.endswith("x86_64"):
            commands = ["-a", "x86_64"]
        elif wheeltag.arch.endswith("arm64"):
            commands = ["-a", "arm64"]
        elif wheeltag.arch.endswith("armv7l"):
            commands = ["-a", "armv7"]
        elif wheeltag.arch.endswith("i686"):
            commands = ["-a", "i386"]

        if wheeltag.arch.endswith("universal2"):
            commands = ["-a", "arm64,x86_64"]
            cmd = (
                [self.xmake, "macro", "-y", "package"]
                + commands
                + ["-f"]
                + split(self.command)
            )
        else:
            cmd = [self.xmake, "config", "-y"] + commands + split(self.command)
            self.run(cmd)
            cmd = [self.xmake, "-y", "--verbose"]
        self.run(cmd)

    def install(self):
        cmd = [self.xmake, "install", "-y", "-o", self.tempname]
        self.run(cmd)

    def check_output(self, cmd: list[str]):
        b = b""
        try:
            b = check_output(cmd, cwd=self.tempname)
        except CalledProcessError as e:
            b: bytes = e.stdout
        return b.decode()

    def show(self):
        cmd = [self.xmake, "show", "-y", "-ltargets", "--json"]
        output = self.check_output(cmd)
        targets = json.loads(output)
        kinds = []
        for target in targets:
            kind = 0
            cmd = [self.xmake, "show", "-y", "-t", target]
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
