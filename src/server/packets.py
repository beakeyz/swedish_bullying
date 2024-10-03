
from ..shared import net

class PacketManager(object):
    
    def __init__(self, lobbyManager) -> None:
        self.lobbyManager = lobbyManager
        
    def HandlePacket(self, connId: int, cm: net.NetworkInterface, netPacket: net.NetPacket):
        '''
        Handle generic server packets
        
        Most packets will be aimed at the lobbymanager, but some packets might need special attention
        TODO: Identify those packets
        '''
        
        assert netPacket.type != net.NetPacketType.INVAL and netPacket.type != net.NetPacketType.PACKET_REJECTED
        
        self.lobbyManager.HandleIncommingPacket(connId, cm, netPacket)
    