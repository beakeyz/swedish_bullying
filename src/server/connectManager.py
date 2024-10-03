from twisted.protocols.socks import SOCKSv4

from ..shared import net
from .debug.log import DebugLog
from .packets import PacketManager

# Connection object that is actually used to store connection information
# 
class InternalServerConnection(object):
    connection: SOCKSv4
    connId: int

    def __init__(self, proto, id) -> None:
        self.connection = proto
        self.connId = id
        
    # Called when this connection is closed
    def destroy(self) -> None:
        pass

# Management Class which is responsible for managaging every single connections
# state
class ConnectionManager(net.NetworkInterface):
    packetManager: PacketManager
    connections: dict[int, InternalServerConnection] = {}
    nextConnId: int
    
    def __init__(self, packetManager) -> None:
        self.nextConnId = 0
        self.packetManager = packetManager
        
    def __newConnectionId(self) -> int:
        next: int = self.nextConnId
        
        # Add one to the next id we want to grab
        self.nextConnId += 1
        
        # Return the previous next
        return next
    
    # Registers a new connection
    #
    # Returns the connection ID of this protocol
    def registerConnection(self, proto: SOCKSv4) -> int:
        id: int = self.__newConnectionId()
        
        # Insert the connection object in our dictionary
        self.connections[id] = InternalServerConnection(proto, id)

        return id
        
    # Called when a connection breaks
    def unregisterConnection(self, connId: int) -> bool:
        connection: InternalServerConnection
        
        try:
            connection = self.connections.pop(connId)
        except KeyError:
            return False
        
        if connection != None:
            connection.destroy()
        
        return True
    
    # Called when we recieve data from a certain connection
    def onDataRecieve(self, connId: int, data: bytes) -> None:
        netPacket: net.packet.NetPacket = net.packet.NetPacket(data=data)
        
        # This would mean invalid packet =(
        # TODO: Send error packet?
        if netPacket.type == net.packet.NetPacketType.INVAL:
            return
        
        DebugLog(f"Recieved data: {data}")
        DebugLog(f"Packet type: {netPacket.type}")
        
        # Let the packet manager handle this packet
        self.packetManager.HandlePacket(connId, self, netPacket)
        
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
    
    def SendPacket(self, connId: int, packet: net.packet.NetPacket) -> int:
        # Marshal the packet into a datastream
        data: bytes = bytes(packet.marshal())
        
        # Beam the steam over the connection
        return self.SendData(connId, data)