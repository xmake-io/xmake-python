# xmake Python build system (PEP 517)

A python build system based on xmake to output sdist/wheel file respecting PEP517.

- [ ] install xmake from PYPI when it cannot be searched in $PATH
- [ ] provide some path (like scikit-build-core's `SKBUILD_PLATLIB_DIR`) to install python binary module (XXX.cpython-313-x86_64-linux-gnu.so)

## Usage

`pyproject.toml`:

```toml
[build-system]
requires = ["xmake-python"]
build-backend = "xmake_python"
```

[example](tests/project/example)

## Introduction

different from other languages, python build system is consist of two parts:

### Frontends

- [build](http://pypi.org/project/build/): `python -m build`
- [uv](https://pypi.org/project/uv/): `uv build`

In charge of:

- install `build-system.requires`
- call `build-system.build-backend`'s `build_wheel()` and `build_sdist()`.

### Backends

Refer
[some python build system backends](https://scikit-build-core.readthedocs.io/en/latest/#other-projects-for-building)

Backend can install optional requires. For example,
[scikit-build-core](https://pypi.org/project/scikit-build-core/)
will install [cmake](http://pypi.org/project/cmake) and [ninja](https://pypi.org/project/ninja/)
only when cmake and ninja are not found in `$PATH`.

We project to provide two python packages. One is a
[wheel for xmake](https://github.com/xmake-io/xmake-wheel/), like cmake and
ninja. Another is a python build system backend, which will install xmake wheel
when xmake is not found in `$PATH`.
