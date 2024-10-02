from .srv import Server
from .connectManager import ConnectionManager
from .packets import PacketManager
from .game.lobby import LobbyManager
from .debug.log import EnableDebug

# Execution starts here
def main():
    print("Server started!")
    
    # Enable/Disable debug messages
    EnableDebug()
        
    lm = LobbyManager()
    
    pm = PacketManager(lm)
    
    # Create a connection manager for this server
    cm = ConnectionManager(pm)
    
    # Actually create the server
    Server(8007, cm)
    
    # Die
    pass

if __name__ == "__main__":
    main()