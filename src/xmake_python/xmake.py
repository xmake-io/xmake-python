from dataclasses import dataclass
from subprocess import run
from pathlib import Path


@dataclass
class XMaker:
    xmake: str = "xmake"
    root: str = "."
    out: str = "."

    def __post_init__(self):
        self.output = str(Path(self.root) / self.out)

    def config(self):
        run([self.xmake, "config", "-P", self.root])

    def build(self):
        run([self.xmake, "-P", self.root, "--verbose"])

    def install(self):
        run([self.xmake, "install", "-P", self.root, "-o", self.out])
