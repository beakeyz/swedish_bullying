from .srv import Server
from .connectManager import ConnectionManager
from .debug.log import EnableDebug

# Execution starts here
def main():
    print("Server started!")
    
    # Enable/Disable debug messages
    EnableDebug()

    # Create a connection manager for this server
    cm = ConnectionManager()
    
    # Actually create the server
    Server(8007, cm)
    
    # Die
    pass

if __name__ == "__main__":
    main()