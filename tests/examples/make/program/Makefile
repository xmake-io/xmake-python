.PHONY: build install
build: main

main: main.c

install:
	install -D main -t $(MAKE_SCRIPTS)
	install -D main.py -t $(MAKE_SCRIPTS)
	install -Dm644 main.h -t $(MAKE_HEADERS)
	install -Dm644 README.md -t $(MAKE_DATA)/share/doc
	install -Dm644 example.py -t $(MAKE_PLATLIB)
	install -Dm644 pyproject.toml -t $(MAKE_METADATA)
	install -Dm644 Makefile -t $(MAKE_NULL)
