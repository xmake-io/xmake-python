# example

Run a frontend:

```sh
$ python -m build -nw
$ ls dist
example-0.0.1-cp313-cp313-linux_x86_64.whl
$ pip install dist/example-0.0.1-cp313-cp313-linux_x86_64.whl
```

```python
>>> from example import py
Hello, python!
>>> from example import c
Hello, cython!
```
