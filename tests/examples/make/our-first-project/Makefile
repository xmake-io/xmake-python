include py.mak
.PHONY: build install

build: our_first_module.$(PYD_EXT)
our_first_module.$(PYD_EXT): our_first_module.c
	$(CC) $(shell pkg-config --cflags python3) -c -o $@ $^

install:
	install -Dm644 our_first_module.$(PYD_EXT) -t $(XMAKE_PLATLIB)
	install -Dm644 README.md -t $(XMAKE_DATA)/share/doc
	install -Dm644 pyproject.toml -t $(XMAKE_METADATA)
	install -Dm644 Makefile -t $(XMAKE_NULL)
