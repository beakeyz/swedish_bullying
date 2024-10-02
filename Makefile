PY=python3
PIP=pip
SRC_DIR=src
SERVER_SRC=$(SRC_DIR)/server
CLIENT_SRC=$(SRC_DIR)/client

DEPS=			\
	twisted 	\
	colorama 	\

server:
	$(PY) $(SERVER_SRC)/main.py

client:
	$(PY) $(CLIENT_SRC)/main.py

$(DEPS):
	$(PIP) install $@

deps: $(DEPS)

.PHONY: server client deps