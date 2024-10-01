from twisted.internet.protocol import Protocol
import server.server as server

# This server implements the twisted internet protocol
class ServerConnection(Protocol):
    srv: server.Server
    connId: int

    def __init__(self, factory, server) -> None:
        self.factory = factory
        self.server = server
        self.connId = -1
        super().__init__()

    def dataReceived(self, data: bytes) -> None:
        print("We've recieved some data!")
        print(f"Len={len(data)}, bytestream={data}")
        return super().dataReceived(data)
    
    def connectionMade(self):
        print("Hey, someone connected to our server!")
        
        # Set this connection ID to an invalid ID
        self.connId = -1

        # Call the server to notify it of this connection
        self.srv.serverMakeConnection()

        return super().connectionMade()