from dataclasses import dataclass
from subprocess import run


@dataclass
class XMaker:
    xmake: str = "xmake"

    def config(self):
        run([self.xmake, "config"])

    def build(self):
        run([self.xmake])

    def install(self):
        run([self.xmake, "install", "-o", "."])
