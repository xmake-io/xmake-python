include ../our-first-project/py.mak
.PHONY: build install

build: example.$(PYD_EXT)
example.$(PYD_EXT): example.cpp
	$(CC) $(shell pkg-config --cflags python3 pybind11) -c -o $@ $^

install:
	install -Dm644 example.$(PYD_EXT) -t $(pythondir)
	install -Dm644 README.md -t $(prefix)/share/doc
	install -Dm644 pyproject.toml -t $(metadatadir)
	install -Dm644 Makefile -t $(nulldir)
