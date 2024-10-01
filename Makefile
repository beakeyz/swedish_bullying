PY=python3
SRC_DIR=src
SERVER_SRC=$(SRC_DIR)/server
CLIENT_SRC=$(SRC_DIR)/client

server:
	$(PY) $(SERVER_SRC)/main.py

client:
	$(PY) $(CLIENT_SRC)/main.py

.PHONY: server client