from twisted.internet.interfaces import IAddress
from twisted.internet.protocol import Protocol, ClientFactory
from twisted.protocols.socks import SOCKSv4

from twisted.internet import reactor

from ...shared.net.packet import NetPacket, NetPacketType

class NetworkProtocol(SOCKSv4):
    
    def connectionMade(self):
        print("NetworkProtocol: connectionMade")
        
        pckt: NetPacket = NetPacket(NetPacketType.JOIN_LOBBY, 0, 1)
        
        data: bytes = bytes(pckt.marshal())
        
        self.write(data)
        
        return super().connectionMade()
    
    def connectionLost(self, reason):
        print("NetworkProtocol: connectionLost")
        return super().connectionLost(reason)
    
    def dataReceived(self, data: bytes) -> None:
        print("NetworkProtocol: dataReceived")
        return super().dataReceived(data)
    
    def write(self, data):
        print("NetworkProtocol: write")
        return super().write(data)

class NetworkClientFact(ClientFactory):
    
    def buildProtocol(self, addr: IAddress) -> Protocol | None:
        return NetworkProtocol()
    
    
class NetworkClient(object):
    
    def __init__(self) -> None:
        self.fact = NetworkClientFact()
        
    def connect(self, host: str, port: int) -> None:
        try:
            # Setup the connection parameters
            reactor.connectTCP(host, port, self.fact)
            
            # Run the connection
            reactor.run()
        except KeyboardInterrupt:
            return