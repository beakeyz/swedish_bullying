from .srv import Server
from .connectManager import ConnectionManager
from .packets import PacketManager
from .game.lobby import LobbyManager
from .debug.log import EnableDebug, OkLog

# Execution starts here
def main():
    port = 8007
    
    # Enable/Disable debug messages
    EnableDebug()
        
    lm = LobbyManager()
    
    OkLog("Initialised lobby manager!")
    
    pm = PacketManager(lm)
    
    OkLog("Initialised packet manager!")
    
    # Create a connection manager for this server
    cm = ConnectionManager(pm)
    
    OkLog(f"Server started at port={port}")
    
    # Actually create the server
    Server(port, cm)
    
    # Die
    pass

if __name__ == "__main__":
    main()