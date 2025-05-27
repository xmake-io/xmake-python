include ../our-first-project/py.mak
.PHONY: build install

build: example.$(PYD_EXT)
example.$(PYD_EXT): example.cpp
	$(CC) $(shell pkg-config --cflags python3 pybind11) -c -o $@ $^

install:
	install -Dm644 example.$(PYD_EXT) -t $(XMAKE_PLATLIB)
	install -Dm644 README.md -t $(XMAKE_DATA)/share/doc
	install -Dm644 pyproject.toml -t $(XMAKE_METADATA)
	install -Dm644 Makefile -t $(XMAKE_NULL)
