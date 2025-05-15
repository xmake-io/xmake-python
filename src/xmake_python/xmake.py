from dataclasses import dataclass
from subprocess import run


@dataclass
class XMaker:
    xmake: str = "xmake"

    def config(self):
        run([self.xmake, "config", "-P", "."])

    def build(self):
        run([self.xmake, "-P", ".", "--verbose"])

    def install(self):
        run([self.xmake, "install", "-P", ".", "-o", "."])
