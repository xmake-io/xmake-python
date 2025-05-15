from dataclasses import dataclass
from subprocess import run


@dataclass
class XMaker:
    xmake: str = "xmake"
    root: str = "."
    out: str = "."

    def config(self):
        run([self.xmake, "config", "-P", self.root])

    def build(self):
        run([self.xmake, "-P", self.root, "--verbose"])

    def install(self):
        run([self.xmake, "install", "-P", self.root, "-o", self.out])
