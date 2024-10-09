from ..packet import *

STARTPACKET_STATUS_OK = 0
STARTPACKET_STATUS_INSUFFICIENT_PLAYERS = 1
STARTPACKET_STATUS_INVAL = 2

class StartPacket(NetPacket):
    status: int | None
    
    def __init__(self) -> None:
        super().__init__(NetPacketType.START_LOBBY, 0, 1, None)
        self.status = STARTPACKET_STATUS_INVAL
        
    def marshal(self) -> bytearray:
        data: bytearray = super().marshal()
        
        data.append(self.status)
        
        return data
    
    def unmarshal(self, data: NetPacketStream):
        if data == None:
            return
        
        super().unmarshal(data)
        
        self.status = data.consume()
        
    def getStatus(self) -> int:
        if self.status == None:
            return STARTPACKET_STATUS_INVAL
        
        return self.status
    
class NotifyActualStartPacket(NetPacket):
    startPlayerId: int

    def __init__(self, startPlayerId) -> None:
        super().__init__(NetPacketType.NOTIFY_START_GAME, NETPACKET_FLAG_CLIENTBOUND, 1, None)
        self.startPlayerId = startPlayerId
        
    def marshal(self) -> bytearray:
        data: bytearray = super().marshal()
        
        data.append(self.startPlayerId)
        
        return data
    
    def unmarshal(self, data: NetPacketStream):
        if data == None:
            return
        
        super().unmarshal(data)
        
        self.startPlayerId = data.consume()