PY=python3
PIP=pip
SRC_DIR=src
SERVER_MOD=$(SRC_DIR).server
CLIENT_MOD=$(SRC_DIR).client

DEPS=			\
	twisted 	\
	colorama 	\

server:
	$(PY) -m $(SERVER_MOD).main

client:
	$(PY) -m $(CLIENT_MOD).main

$(DEPS):
	$(PIP) install $@

deps: $(DEPS)

.PHONY: server client deps