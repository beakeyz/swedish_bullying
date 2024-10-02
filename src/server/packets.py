
from ..shared.net.packet import NetPacket, NetPacketType

class PacketManager(object):
    
    def __init__(self, lobbyManager) -> None:
        self.lobbyManager = lobbyManager
        
    def HandlePacket(self, connId: int, cm, netPacket: NetPacket):
        '''
        Handle generic server packets
        
        Most packets will be aimed at the lobbymanager, but some packets might need special attention
        TODO: Identify those packets
        '''
        
        assert netPacket.type != NetPacketType.INVAL and netPacket.type != NetPacketType.PACKET_REJECTED
        
        self.lobbyManager.HandleIncommingPacket(connId, cm, netPacket)
    