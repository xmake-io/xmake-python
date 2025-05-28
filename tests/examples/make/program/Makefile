.PHONY: build install
build: main
main: main.c main.h
main.h:
	echo '#define VERSION "$(project_version)"' > $@

install:
	install -D main -t $(bindir)
	install -D main.py -t $(bindir)
	install -Dm644 main.h -t $(includedir)
	install -Dm644 README.md -t $(prefix)/share/doc
	install -Dm644 example.py -t $(pythondir)
	install -Dm644 pyproject.toml -t $(metadatadir)
	install -Dm644 Makefile -t $(nulldir)
