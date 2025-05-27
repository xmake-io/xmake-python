include ../our-first-project/py.mak
.PHONY: build install

build: c.$(PYD_EXT)
c.c: c.py
	cython -3 -o $@ $^
c.$(PYD_EXT): c.c
	$(CC) $(shell pkg-config --cflags python3) -c -o $@ $^

install:
	install -Dm644 c.$(PYD_EXT) -t $(XMAKE_PLATLIB)/example
	install -Dm644 src/example/py.py -t $(XMAKE_PLATLIB)/example
	install -Dm644 README.md -t $(XMAKE_DATA)/share/doc
	install -Dm644 pyproject.toml -t $(XMAKE_METADATA)
	install -Dm644 Makefile -t $(XMAKE_NULL)
