import json
import os
from dataclasses import dataclass
from pathlib import Path
from shlex import join, split
from subprocess import run

from ._logging import rich_print
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

    def run(self, commands, check: bool = True):
        cwd = self.tempname
        eol = "\n"
        if os.name == "nt":
            eol = "\r" + eol
        rich_print(
            f"{{bold}}$ cd {cwd}{eol}$ " + join(commands), color="green"
        )
        process = run(
            commands,
            cwd=cwd,
            check=check,
            text=True,
            capture_output=(not check),
        )
        if not check:
            print(process.stdout, end="")
        return process.stdout

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
                [self.xmake, "macro", "-y", "-P", self.tempname, "package"]
                + commands
                + ["-f"]
                + split(self.command)
            )
        else:
            cmd = (
                [self.xmake, "config", "-y", "-P", self.tempname]
                + commands
                + split(self.command)
            )
            self.run(cmd)
            cmd = [self.xmake, "-y", "-P", self.tempname, "--verbose"]
        self.run(cmd)

    def install(self):
        cmd = [
            self.xmake,
            "install",
            "-y",
            "-P",
            self.tempname,
            "--verbose",
            "-o",
            self.tempname,
        ]
        self.run(cmd)

    def show(self):
        cmd = [
            self.xmake,
            "show",
            "-y",
            "-P",
            self.tempname,
            "-ltargets",
            "--json",
        ]
        output = self.run(cmd, False)
        targets = []
        try:
            targets = json.loads(output)
        except json.decoder.JSONDecodeError:
            print(f"{output}")
        kinds = []
        for target in targets:
            kind = 0
            cmd = [self.xmake, "show", "-y", "-P", self.tempname, "-t", target]
            text = self.run(cmd, False)
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
