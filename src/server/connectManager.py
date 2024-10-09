from twisted.protocols.socks import SOCKSv4

from ..shared import net
from .debug.log import DebugLog
from .packets import PacketManager

# Connection object that is actually used to store connection information
# 
class InternalServerConnection(object):
    connection: SOCKSv4
    connId: int
    # Flag to mark if the connection is clear. This is a weird hack to solidify communication
    # Between client and server. For every packet the server sends to the client, the client (should) respond(s)
    # with a OK_PING packet. Only after the server recieves this, it can send the next packet
    pipeClear: bool
    # Queue to store any packets the server wants to send to a client, while it hasn't yet sent an
    # OK_PING packet back
    packetQueue: list

    def __init__(self, proto, id) -> None:
        self.connection = proto
        self.connId = id
        self.pipeClear = True
        self.packetQueue = []
        
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
        
        # Synthesise a leave packet here
        leavePacket: net.LeavePacket = net.LeavePacket()
        
        self.packetManager.HandlePacket(connId, self, leavePacket)
        
        if connection != None:
            connection.destroy()
                    
        return True
    
    # Called when we recieve data from a certain connection
    def onDataRecieve(self, connId: int, data: bytes) -> None:
        data = net.NetPacketStream(data)
        netPacket: net.packet.NetPacket = net.packet.NetPacket(data=data)
        
        # This would mean invalid packet =(
        # TODO: Send error packet?
        if netPacket.type == net.packet.NetPacketType.INVAL:
            return
        
        DebugLog(f"Recieved data: {data}")
        DebugLog(f"Packet type: {netPacket.type}")
        
        # Skip any OK packets we recieve
        if netPacket.type == net.packet.NetPacketType.OK_PING:
            self.connections[connId].pipeClear = True
            
            # Try to send any queued packets that have been waiting
            try:
                p = self.connections[connId].packetQueue.pop(0)
                
                # Send a queued packet
                self.SendPacket(connId, p)
            except:
                pass
            return
        
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
        
        # If the connection isn't clear, queue the packet
        if self.connections[connId].pipeClear == False:
            self.connections[connId].packetQueue.append(packet)
            return -1
        
        # Marshal the packet into a datastream
        data: bytes = bytes(packet.marshal())
        
        # Mark the pipe as not clear
        self.connections[connId].pipeClear = False
        
        # Beam the steam over the connection
        return self.SendData(connId, data)