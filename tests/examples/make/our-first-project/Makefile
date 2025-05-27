include py.mak
.PHONY: build install

build: our_first_module.$(PYD_EXT)
our_first_module.$(PYD_EXT): our_first_module.c
	$(CC) $(shell pkg-config --cflags python3) -c -o $@ $^

install:
	install -Dm644 our_first_module.$(PYD_EXT) -t $(pythondir)/our_first_project
	install -Dm644 README.md -t $(prefix)/share/doc
	install -Dm644 pyproject.toml -t $(metadatadir)
	install -Dm644 Makefile -t $(nulldir)
