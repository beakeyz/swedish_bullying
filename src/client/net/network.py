import time

from twisted.internet.interfaces import IAddress
from twisted.internet.protocol import Protocol, ClientFactory
from twisted.protocols.socks import SOCKSv4

from twisted.internet import reactor, threads

from ...shared.net.packet import NetPacket, NetPacketType, NETPACKET_FLAG_EXPECT_RESP
from ...shared.net.netif import NetworkInterface

class NetworkProtocol(SOCKSv4):
    netif: NetworkInterface
    
    def __init__(self, netif: NetworkInterface, logging=None, reactor=...):
        # Set the network client object of this protocol connection
        self.netif = netif
        super().__init__(logging, reactor)
    
    def connectionMade(self):
        print("NetworkProtocol: connectionMade")
        
        # Notify the network client of our existance
        self.netif.SetProtocol(self)
        
        return super().connectionMade()
    
    def connectionLost(self, reason):
        print("NetworkProtocol: connectionLost")
        
        self.netif.disconnect(0)
        
        return super().connectionLost(reason)
    
    def dataReceived(self, data: bytes) -> None:
        # Grab the netpacket
        netPacket: NetPacket = NetPacket(data=data)
        
        # Invalid data
        if netPacket.type == NetPacketType.INVAL:
            return
        
        if netPacket.isNotifyPacket():
            self.netif.QueueNotifyPacket(netPacket)
        # Let the server know this packet was rejected if the response queue is blocked...
        elif self.netif.QueueResponsePacket(0, netPacket) < 0:
            self.netif.SendPacket(0, NetPacket(NetPacketType.PACKET_REJECTED, 0, 1))
        
    
    def write(self, data):
        print("NetworkProtocol: write")
        return super().write(data)

class NetworkClientFact(ClientFactory):
        
    def __init__(self, networkClient) -> None:
        self.networkClient = networkClient
        super().__init__()
    
    def buildProtocol(self, addr: IAddress) -> Protocol | None:
        return NetworkProtocol(self.networkClient)
    
    
class NetworkClient(NetworkInterface):
    responsePackets: list[NetPacket] = []
    connectionProtocol: NetworkProtocol = None
    
    def __init__(self, game) -> None:
        self.fact = NetworkClientFact(self)
        self.game = game
        
    def connect(self, host: str, port: int, clientThread, notifyThread) -> None:
        # Check if we're already connected
        if self.isConnected():
            return
        
        try:
            # Setup the connection parameters
            reactor.connectTCP(host, port, self.fact)
            
            threads.deferToThread(clientThread, self)
            
            threads.deferToThread(notifyThread, self)
            
            # Run the connection
            reactor.run()
        except KeyboardInterrupt:
            return
        
    def disconnect(self, connId: int) -> int:
        _tmpConn: NetworkProtocol
        
        if not self.isConnected():
            return -1
        
        # Cache the connection protocol
        _tmpConn = self.GetProtocol()
        
        # Clear the protocol field first
        self.SetProtocol(None)
        
        if _tmpConn:
            # Lose the connection (Didn't want it anyway)
            _tmpConn.transport.loseConnection()
        
        # Stop the reactor
        reactor.stop()
        
        return 0
        
    def isConnected(self) -> bool:
        return self.GetProtocol() != None
    
    def QueueResponsePacket(self, connId: int, packet: NetPacket) -> int:
        # Check if the queue is blocked
        if len(self.responsePackets):
            return -1
            
        # Enqueue this bitch
        self.responsePackets.append(packet)
        
        return 0
        
    def SendPacket(self, connId: int, netPacket: NetPacket) -> int:
        if not self.isConnected():
            return -1
        
        # Marshal the packet into a data stream
        data: bytearray = netPacket.marshal()
        
        # Beam the stream over the connection
        self.GetProtocol().write(bytes(data))
        
        return 0
    
    def SendPacketAndAwaitResponse(self, netPacket: NetPacket) -> NetPacket | None:
        timeout: int = 5_000
        
        if self.SendPacket(0, netPacket) < 0:
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