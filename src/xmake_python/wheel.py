from __future__ import annotations
import argparse
from base64 import urlsafe_b64encode
import contextlib
from datetime import datetime, timezone
import hashlib
from io import StringIO
import logging
import os
import os.path as osp
import stat
import tempfile
from pathlib import Path
from types import SimpleNamespace
import zipfile
from pathlib import Path

from . import common
from .__main__ import __version__
from .xmake import XMaker
from .builder.wheel_tag import WheelTag

log = logging.getLogger(__name__)

wheel_file_template = """\
Wheel-Version: 1.0
Generator: xmake {version}
Root-Is-Purelib: true
""".format(version=__version__)

def _write_wheel_file(f, supports_py2=False):
    f.write(wheel_file_template)
    if supports_py2:
        f.write("Tag: py2-none-any\n")
    f.write("Tag: py3-none-any\n")


def _set_zinfo_mode(zinfo, mode):
    # Set the bits for the mode
    zinfo.external_attr = mode << 16


def zip_timestamp_from_env() -> tuple[int, int, int, int, int, int] | None:
    """Prepare a timestamp from $SOURCE_DATE_EPOCH, if set"""
    try:
        # If SOURCE_DATE_EPOCH is set (e.g. by Debian), it's used for
        # timestamps inside the zip file.
        t = int(os.environ['SOURCE_DATE_EPOCH'])
        d = datetime.fromtimestamp(t, timezone.utc)
    except (KeyError, ValueError):
        # Otherwise, we'll use the mtime of files, and generated files will
        # default to 2016-1-1 00:00:00
        return None

    if d.year >= 1980:
        log.info("Zip timestamps will be from SOURCE_DATE_EPOCH: %s", d)
        # zipfile expects a 6-tuple, not a datetime object
        return d.year, d.month, d.day, d.hour, d.minute, d.second
    else:
        log.info("SOURCE_DATE_EPOCH is below the minimum for zip file timestamps")
        log.info("Zip timestamps will be 1980-01-01 00:00:00")
        return 1980, 1, 1, 0, 0, 0


class WheelBuilder:
    def __init__(
            self, directory, module, metadata, entrypoints, target_fp, data_directory, xmake = None
    ):
        """Build a wheel from a module/package
        """
        self.directory = directory
        self.module = module
        self.metadata = metadata
        self.entrypoints = entrypoints
        self.data_directory = data_directory

        self.records = []
        self.source_time_stamp = zip_timestamp_from_env()

        # Open the zip file ready to write
        self.wheel_zip = None
        # skip creating wheel for get_requires_for_build_wheel()
        if target_fp is not None:
            self.wheel_zip = zipfile.ZipFile(target_fp, 'w',
                                 compression=zipfile.ZIP_DEFLATED)
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.data = self.root / "data"
        if xmake:
            xmake.tempname = self.temp.name
        self.xmake = xmake
        self.is_build = False

    @classmethod
    def from_ini_path(cls, ini_path, target_fp):
        from .config import read_xmake_config
        directory = ini_path.parent
        ini_info = read_xmake_config(ini_path)
        entrypoints = ini_info.entrypoints
        module = common.Module(ini_info.module, directory)
        metadata = common.make_metadata(module, ini_info)
        xmake = None
        xmaker = ini_info.dtool.get("xmaker", {})
        xmake_path = directory / "xmake.lua"
        if xmake_path.exists() or xmaker != {}:
            xmake = XMaker(xmaker.get("xmake", "xmake"),
                           xmaker.get("command", ""),
                           xmaker.get("tempname", ""),
                           xmaker.get("project", os.path.abspath(".")))
        return cls(
            directory, module, metadata, entrypoints, target_fp, ini_info.data_directory, xmake
        )

    @property
    def dist_info(self):
        return common.dist_info_name(self.metadata.name, self.metadata.version)

    @property
    def wheel_filename(self):
        dist_name = common.normalize_dist_name(self.metadata.name, self.metadata.version)
        py_api = ""
        root_is_purelib = True
        if self.xmake and self.is_build:
            root_is_purelib = False
            with open("xmake.lua") as f:
                text = f.read()
            if text.find('add_rules("python') == text.find("add_rules('python") == -1:
                py_api = ('py2.' if self.metadata.supports_py2 else '') + 'py3'
        tag = str(WheelTag.compute_best([], py_api, root_is_purelib=root_is_purelib))
        return '{}-{}.whl'.format(dist_name, tag)

    def _add_file(self, full_path, rel_path):
        log.debug("Adding %s to zip file", full_path)
        full_path, rel_path = str(full_path), str(rel_path)
        if os.sep != '/':
            # We always want to have /-separated paths in the zip file and in
            # RECORD
            rel_path = rel_path.replace(os.sep, '/')

        if self.source_time_stamp is None:
            zinfo = zipfile.ZipInfo.from_file(full_path, rel_path)
        else:
            # Set timestamps in zipfile for reproducible build
            zinfo = zipfile.ZipInfo(rel_path, self.source_time_stamp)

        # Normalize permission bits to either 755 (executable) or 644
        st_mode = os.stat(full_path).st_mode
        new_mode = common.normalize_file_permissions(st_mode)
        _set_zinfo_mode(zinfo, new_mode & 0xFFFF)  # Unix attributes

        if stat.S_ISDIR(st_mode):
            zinfo.external_attr |= 0x10  # MS-DOS directory flag

        zinfo.compress_type = zipfile.ZIP_DEFLATED

        hashsum = hashlib.sha256()
        if self.wheel_zip:
            with open(full_path, 'rb') as src, self.wheel_zip.open(zinfo, 'w') as dst:
                while True:
                    buf = src.read(1024 * 8)
                    if not buf:
                        break
                    hashsum.update(buf)
                    dst.write(buf)

        size = os.stat(full_path).st_size
        hash_digest = urlsafe_b64encode(hashsum.digest()).decode('ascii').rstrip('=')
        self.records.append((rel_path, hash_digest, size))

    @contextlib.contextmanager
    def _write_to_zip(self, rel_path, mode=0o644):
        sio = StringIO()
        yield sio

        log.debug("Writing data to %s in zip file", rel_path)
        # The default is a fixed timestamp rather than the current time, so
        # that building a wheel twice on the same computer can automatically
        # give you the exact same result.
        date_time = self.source_time_stamp or (2016, 1, 1, 0, 0, 0)
        zi = zipfile.ZipInfo(rel_path, date_time)
        # Also sets bit 0x8000 for "regular file" (S_IFREG)
        _set_zinfo_mode(zi, mode | stat.S_IFREG)
        b = sio.getvalue().encode('utf-8')
        hashsum = hashlib.sha256(b)
        hash_digest = urlsafe_b64encode(hashsum.digest()).decode('ascii').rstrip('=')
        if self.wheel_zip:
            self.wheel_zip.writestr(zi, b, compress_type=zipfile.ZIP_DEFLATED)
        self.records.append((rel_path, hash_digest, len(b)))

    def copy_module(self):
        log.info('Copying package file(s) from %s', self.module.path)

        for full_path in common.walk_data_dir(self.root / "platlib"):
            rel_path = os.path.relpath(full_path, self.root / "platlib")
            self._add_file(full_path, rel_path)

    def add_pth(self):
        with self._write_to_zip(self.module.name + ".pth") as f:
            f.write(str(self.module.source_dir.resolve()))

    def add_data_directory(self):
        dir_in_whl = '{}.data/data/'.format(
            common.normalize_dist_name(self.metadata.name, self.metadata.version)
        )
        for full_path in common.walk_data_dir(self.data_directory):
            rel_path = os.path.relpath(full_path, self.data_directory)
            self._add_file(full_path, dir_in_whl + rel_path)
        if not self.data.exists():
            return
        for name in os.listdir(self.data):
            if name in {"bin", "include"}:
                continue
            for full_path in common.walk_data_dir(self.data / name):
                rel_path = os.path.relpath(full_path, self.data).partition(name + os.path.sep)[2]
                self._add_file(full_path, dir_in_whl + name + os.path.sep + rel_path)

    def add_scripts_directory(self):
        dir_in_whl = '{}.data/scripts/'.format(
            common.normalize_dist_name(self.metadata.name, self.metadata.version)
        )
        for full_path in common.walk_data_dir(Path(self.data) / "bin"):
            rel_path = os.path.relpath(full_path, Path(self.data) / "bin")
            self._add_file(full_path, dir_in_whl + rel_path)

    def add_headers_directory(self):
        dir_in_whl = '{}.data/headers/'.format(
            common.normalize_dist_name(self.metadata.name, self.metadata.version)
        )
        for full_path in common.walk_data_dir(Path(self.data) / "include"):
            rel_path = os.path.relpath(full_path, Path(self.data) / "include")
            self._add_file(full_path, dir_in_whl + rel_path)

    def write_metadata(self):
        log.info('Writing metadata files')

        if self.entrypoints:
            with self._write_to_zip(self.dist_info + '/entry_points.txt') as f:
                common.write_entry_points(self.entrypoints, f)

        for file in self.metadata.license_files:
            self._add_file(self.directory / file, '%s/licenses/%s' % (self.dist_info, file))
        for full_path in common.walk_data_dir(self.root / "metadata"):
            rel_path = os.path.relpath(full_path, self.root / "metadata")
            self._add_file(full_path, '%s/%s' % (self.dist_info, rel_path))

        with self._write_to_zip(self.dist_info + '/WHEEL') as f:
            _write_wheel_file(f, supports_py2=self.metadata.supports_py2)

        with self._write_to_zip(self.dist_info + '/METADATA') as f:
            self.metadata.write_metadata_file(f)

    def write_record(self):
        log.info('Writing the record of files')
        # Write a record of the files in the wheel
        with self._write_to_zip(self.dist_info + '/RECORD') as f:
            for path, hash, size in self.records:
                f.write('{},sha256={},{}\n'.format(path, hash, size))
            # RECORD itself is recorded with no hash or size
            f.write(self.dist_info + '/RECORD,,\n')

    def build(self, editable=False):
        with self.temp:
            if self.xmake:
                self.xmake.config()
                self.xmake.build()
                self.xmake.install()
                if os.path.isdir("build"):
                    self.is_build = True
            try:
                if editable:
                    self.add_pth()
                else:
                    self.copy_module()
                self.add_data_directory()
                self.add_scripts_directory()
                self.add_headers_directory()
                self.write_metadata()
                self.write_record()
            finally:
                if self.wheel_zip:
                    self.wheel_zip.close()

def make_wheel_in(ini_path, wheel_directory, editable=False):
    # We don't know the final filename until metadata is loaded, so write to
    # a temporary_file, and rename it afterwards.
    (fd, temp_path) = tempfile.mkstemp(suffix='.whl', dir=str(wheel_directory))
    try:
        with open(fd, 'w+b') as fp:
            wb = WheelBuilder.from_ini_path(ini_path, fp)
            wb.build(editable)

        wheel_path = wheel_directory / wb.wheel_filename
        os.replace(temp_path, str(wheel_path))
    except:
        os.unlink(temp_path)
        raise

    log.info("Built wheel: %s", wheel_path)
    return SimpleNamespace(builder=wb, file=wheel_path)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'srcdir',
        type=Path,
        nargs='?',
        default=Path.cwd(),
        help='source directory (defaults to current directory)',
    )

    parser.add_argument(
        '--outdir',
        '-o',
        help='output directory (defaults to {srcdir}/dist)',
    )
    args = parser.parse_args(argv)
    outdir = args.srcdir / 'dist' if args.outdir is None else Path(args.outdir)
    print("Building wheel from", args.srcdir)
    pyproj_toml = args.srcdir / 'pyproject.toml'
    outdir.mkdir(parents=True, exist_ok=True)
    info = make_wheel_in(pyproj_toml, outdir)
    print("Wheel built", outdir / info.file.name)

if __name__ == "__main__":
    main()
