.PHONY: build install
build: main

main: main.c

install:
	install -D main -t $(XMAKE_SCRIPTS)
	install -D main.py -t $(XMAKE_SCRIPTS)
	install -Dm644 main.h -t $(XMAKE_HEADERS)
	install -Dm644 README.md -t $(XMAKE_DATA)/share/doc
	install -Dm644 example.py -t $(XMAKE_PLATLIB)
	install -Dm644 pyproject.toml -t $(XMAKE_METADATA)
	install -Dm644 Makefile -t $(XMAKE_NULL)
