# xmake Python build system (PEP 517)

A python build system based on xmake to output sdist/wheel file respecting PEP517.

## Related Projects

Currently, the methods to build a python wheel containing C/C++ code are as
following:

- [distutils](http://pypi.org/project/distutils/): A simple C/C++ build system
  written in pure python. Before python 3.13, it is one of python standard
  libraries. Slow.
  - [setuptools](http://pypi.org/project/setuptools/): default python build
    system, which can use distutils to build python/C mixed project.
- [scons](https://pypi.org/project/SCons/): A C/C++ build system written in pure
  python. It is very slow. So Evan Martin, the maintainer of google chrome, has
  to create ninja and
  [switch](https://neugierig.org/software/chromium/notes/2011/02/ninja.html)
  chrome's build system to ninja.
  - [enscons](https://pypi.org/project/enscons/): A python build system based
    on scons. Advantage: no extra dependency except python.
- [cmake](https://pypi.org/project/cmake/): A classic C/C++ build system. A
  standard in fact while bad-designed syntax.
  [scikit-build](https://github.com/scikit-build/) organization package it to
  PYPI to let python developer enjoy it. cmake in PYPI uses
  [ninja](https://pypi.org/project/ninja/) as its backend, which is also
  packaged by scikit-build organization. That means that python, cmake, ninja is
  needed. Although the latter two will be installed from PYPI.
  - [scikit-build](https://pypi.org/project/scikit-build/): first python build
    system based on cmake developed by scikit-build organization. Replaced by
    scikit-build-core.
  - [scikit-build-core](https://pypi.org/project/scikit-build-core/):
    scikit-build organization recommends it.
  - [cmeel](https://pypi.org/project/cmeel/): Another wheel.
  - [py-build-cmake](https://pypi.org/project/py-build-cmake/): Another wheel
    forked from [flit](https://pypi.org/project/flit/).
- [meson](https://pypi.org/project/meson/): A C/C++ build system written in pure
  python. However, it uses ninja as its backend.
  - [meson-python](https://pypi.org/project/meson-python/): A python build
    system based on meson.

Except slow distutils/scons, both cmake and meson use ninja as their backend. So
if a python developer want to build a python/C mixed project in high speed,
ninja is the only one choice. We hope xmake can be another choice -- it
should be as fast as ninja, as easy as meson, as powerful as cmake.

- [xmake](https://pypi.org/project/xmake-wheel):
  [package it](https://github.com/xmake-io/xmake-wheel/) to PYPI.
  - [xmake-python](https://pypi.org/project/xmake-python/): A python build system
    based on xmake. This project!

## TODO

- [ ] get project version from `xmake.lua`
- [ ] know wheel tag by rules <https://github.com/xmake-io/xmake/discussions/6499>.
  Currently, we find `add_rules(['"]python\.` in `xmake.lua`, which is not
  precious.

## Usage

`pyproject.toml`:

```toml
[build-system]
requires = ["xmake-python"]
build-backend = "xmake_python"
```

[examples](tests/examples)

## Introduction

Python build system support build sdist, wheel and editable installation.
According to [PEP517](https://peps.python.org/pep-0517/), python build system
is consist of two parts:

### Frontends

- `pyproject-build`/[`python -m build`](http://pypi.org/project/build/):
  standard realization.
- [`uv build`](https://pypi.org/project/uv/): the fastest frontend currently.
- [`pip wheel`](https://github.com/pypa/pip/): pip is an incomplete frontend
  because build sdist is still a
  [feature request](https://github.com/pypa/pip/issues/3513).

In charge of:

- install required build dependencies from `build-system.requires`
- install optional build dependencies from the result of calling
  `build-system.build-backend`'s `get_requires_for_build_{sdist,wheel,editable}()`
- call `build-system.build-backend`'s `build_{sdist,wheel,editable}()`

### Backends

Refer
[some python build system backends](https://scikit-build-core.readthedocs.io/en/latest/#other-projects-for-building)

Backend can install optional build dependencies. For example,
[scikit-build-core](https://pypi.org/project/scikit-build-core/)
will install [cmake](http://pypi.org/project/cmake) and [ninja](https://pypi.org/project/ninja/)
only when cmake and ninja are not found in `$PATH`.

We provide two python packages. One is a
[wheel for xmake](https://github.com/xmake-io/xmake-wheel/), like cmake and
ninja. Another is a python build system backend, which will install xmake wheel
when xmake is not found in `$PATH`.

### Wheel

Python package's format is wheel, which is a zip file naturally. If you try
create a wheel file named `example-0.0.1-cp313-cp313-linux_x86_64.whl`, it
optionally contains these files, and they will be installed to:

- python module, can be pure python files or dynamic linked library
  - `example.py`: `/usr/lib/python3.13/site-packages/example.py`
  - `example/__init__.py`: `/usr/lib/python3.13/site-packages/example/__init__.py`
  - `example.cpython-313-x86_64-linux-gnu.so`: `/usr/lib/python3.13/site-packages/example.cpython-313-x86_64-linux-gnu.so`
  - `example/_C.cpython-313-x86_64-linux-gnu.so`: `/usr/lib/python3.13/site-packages/example/_C.cpython-313-x86_64-linux-gnu.so`
- attached data
  - `example-0.0.1.data/scripts/example`: `/usr/bin/example`
  - `example-0.0.1.data/headers/example.h`: `/usr/include/python3.13/example/example.h`
  - `example-0.0.1.data/data/other/data.txt`: `/usr/other/data.txt`
- metadata
  - `example-0.0.1.dist-info/WHEEL`: `/usr/lib/python3.13/site-packages/example-0.0.1.dist-info/WHEEL`
  - `example-0.0.1.dist-info/METADATA`: `/usr/lib/python3.13/site-packages/example-0.0.1.dist-info/METADATA`
  - `example-0.0.1.dist-info/RECORD`: `/usr/lib/python3.13/site-packages/example-0.0.1.dist-info/RECORD`
  - `example-0.0.1.dist-info/licenses/LICENSE`: `/usr/lib/python3.13/site-packages/example-0.0.1.dist-info/licenses/LICENSE`

So we create a [xmake.lua](src/xmake_python/templates/xmake.lua), which defines
some variables, and when `xmake install -o/tmp/tmpXXXXXXXX`, they will be
some paths prefixed with `/tmp/tmpXXXXXXXX`, and finally packaged to:

- xmake-platlib: `/platlib` -> `/tmp/tmpXXXXXXXX/platlib` -> `/`
- xmake-scripts: `/data/bin` -> `/tmp/tmpXXXXXXXX/data/bin` ->
  `example-0.0.1.data/scripts/`
- xmake-headers: `/data/include` -> `/tmp/tmpXXXXXXXX/data/include` ->
  `example-0.0.1.data/headers/`
- xmake-data: `/data` -> `/tmp/tmpXXXXXXXX/data` ->
  `example-0.0.1.data/data/`
- xmake-metadata: `/metadata` -> `/tmp/tmpXXXXXXXX/metadata` ->
  `example-0.0.1.dist-info/`
- xmake-null: `/null` -> `/tmp/tmpXXXXXXXX/null` -> will not be packaged

So you can create 3 kinds packages:

- pure python wheel, which named like `example-0.0.1-py3-none-any.whl`,
  support any platforms and python 3 version.
- contains binary program, which named like
  `example-0.0.1-py3-none-linux_x86_64.whl`, support fixed platforms, python3
  version. Because different OS and cpu cannot mix binary programs and
  dynamically linked libraries.
- dynamic linked python module, which named like
  `example-0.0.1-cp313-cp313-linux_x86_64.whl`, because dynamic linked python
  module links different python library `/usr/lib/libpython3.X.so`
