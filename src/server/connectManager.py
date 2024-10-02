from twisted.protocols.socks import SOCKSv4

class InternalServerConnection(object):
    connection: SOCKSv4
    connId: int

    def __init__(self, proto) -> None:
        self.connection = proto

# Management Class which is responsible for managaging every single connections
# state
class ConnectionManager(object):
    connections: dict[int, InternalServerConnection] = {}
    nextConnId: int
    
    def __init__(self) -> None:
        self.nextConnId = 0
    
    # Registers a new connection
    #
    # Returns the connection ID of this protocol
    def registerConnection(self, proto: SOCKSv4) -> int:
        pass
    
    # Called when a connection breaks
    def unregisterConnection(self, connId: int) -> bool:
        pass
    
    # Called when we recieve data from a certain connection
    def onDataRecieve(self, connId: int, data: bytes) -> None:
        pass
    
    # Called when the server wants to send some data back to the client
    # (Most of the time through ConnectionManager->SendData)
    def onDataSend(self, connId: int, data: bytes) -> None:
        pass
    
    # Utility function to make responses
    #
    # Returns a negative error code if the connectionID is invalid
    # Caller should handle this case appropriately
    def SendData(self, connId: int, data: bytes) -> int:
        connection: InternalServerConnection = self.connections[connId];
        
        if connection == None:
            return -1
        
        # Write over the connection
        connection.connection.write(data)
        return 0