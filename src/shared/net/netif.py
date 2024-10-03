from twisted.protocols.socks import SOCKSv4
from .packet import NetPacket

# Semi-abstract class that can be implemented both on the serverside, as well
# as the clientside
#
# The server will make use of the connId field, the client most likely won't
class NetworkInterface(object):
    protocol: SOCKSv4 = None
    responsePackets: dict[int, list[NetPacket]] = {}
    
    # Abstract function
    def SendPacket(self, connId: int, packet: NetPacket) -> int:
        pass
    
    def QueueResponsePacket(self, connId: int, packet: NetPacket) -> int:
        if self.responsePackets.get(connId) == None:
            self.responsePackets[connId] = []
            
        self.responsePackets[connId].append(packet)
    
    # Abstract function
    def SetProtocol(self, proc: SOCKSv4) -> int:
        self.protocol = proc
        
    def GetProtocol(self) -> SOCKSv4:
        return self.protocol
    