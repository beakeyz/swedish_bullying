import time

from twisted.internet.interfaces import IAddress
from twisted.internet.protocol import Protocol, ClientFactory
from twisted.protocols.socks import SOCKSv4

from twisted.internet import reactor, threads

from ...shared.net.packet import NetPacket, NetPacketType, NETPACKET_FLAG_EXPECT_RESP

class NetworkProtocol(SOCKSv4):
    
    def __init__(self, networkClient, logging=None, reactor=...):
        # Set the network client object of this protocol connection
        self.networkClient = networkClient
        super().__init__(logging, reactor)
    
    def connectionMade(self):
        print("NetworkProtocol: connectionMade")
        
        # Notify the network client of our existance
        self.networkClient.connectionProtocol = self
        
        return super().connectionMade()
    
    def connectionLost(self, reason):
        print("NetworkProtocol: connectionLost")
        return super().connectionLost(reason)
    
    def dataReceived(self, data: bytes) -> None:
        print(f"NetworkProtocol: dataReceived {data.decode()}")
        
        # Grab the netpacket
        netPacket: NetPacket = NetPacket(data=data)
        
        # Invalid data
        if netPacket.type == NetPacketType.INVAL:
            return super().dataRecieved(data)
        
        # Let the server know this packet was rejected if the response queue is blocked...
        if not self.networkClient.queueResponsePacket(netPacket):
            self.networkClient.SendPacket(NetPacket(NetPacketType.PACKET_REJECTED, 0, 1))
            return super().dataRecieved(data)
        
        return super().dataReceived(data)
    
    def write(self, data):
        print("NetworkProtocol: write")
        return super().write(data)

class NetworkClientFact(ClientFactory):
        
    def __init__(self, networkClient) -> None:
        self.networkClient = networkClient
        super().__init__()
    
    def buildProtocol(self, addr: IAddress) -> Protocol | None:
        return NetworkProtocol(self.networkClient)
    
    
class NetworkClient(object):
    responsePackets: list[NetPacket] = []
    connectionProtocol: NetworkProtocol = None
    
    def __init__(self) -> None:
        self.fact = NetworkClientFact(self)
        
    def connect(self, host: str, port: int, clientThread) -> None:
        # Check if we're already connected
        if self.isConnected():
            return
        
        try:
            # Setup the connection parameters
            reactor.connectTCP(host, port, self.fact)
            
            threads.deferToThread(clientThread, self)
            
            # Run the connection
            reactor.run()
        except KeyboardInterrupt:
            return
        
    def disconnect(self) -> bool:
        _tmpConn: NetworkProtocol
        
        if not self.isConnected:
            return False
        
        # Cache the connection protocol
        _tmpConn = self.connectionProtocol
        
        # Clear the protocol field first
        self.connectionProtocol = None
        
        # Lose the connection (Didn't want it anyway)
        _tmpConn.transport.loseConnection()
        
        # Stop the reactor
        reactor.stop()
        
    def isConnected(self) -> bool:
        return self.connectionProtocol != None
    
    def queueResponsePacket(self, netPacket: NetPacket) -> bool:
        # Check if the queue is blocked
        if len(self.responsePackets):
            return False
            
        # Enqueue this bitch
        self.responsePackets.append(netPacket)
        
        return True
        
    def SendPacket(self, netPacket: NetPacket) -> bool:
        if not self.isConnected():
            return False
        
        # Marshal the packet into a data stream
        data: bytearray = netPacket.marshal()
        
        # Beam the stream over the connection
        self.connectionProtocol.write(bytes(data))
        
        return True
    
    def SendPacketAndAwaitResponse(self, netPacket: NetPacket) -> NetPacket | None:
        timeout: int = 5_000
        
        if netPacket.hasFlags(NETPACKET_FLAG_EXPECT_RESP) == False:
            return None
        
        if not self.SendPacket(netPacket):
            return None
        
        # Sleep until there is a response packet for us
        # Give it a timeout of 5 seconds, after which we auto leave
        while not len(self.responsePackets) and timeout:
            time.sleep(0.001)
            timeout -= 1
        
        if not timeout:
            return None
            
        # Remove this item
        return self.responsePackets.pop(0)
    
    def PollResponsePackets(self) -> NetPacket | None:
        # Don't do anything is there is nothing in the response list
        if not len(self.responsePackets):
            return None
        
        # Yoink that fucker
        return self.responsePackets.pop(0)