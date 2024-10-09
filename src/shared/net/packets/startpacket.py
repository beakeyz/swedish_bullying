from ..packet import *

STARTPACKET_STATUS_OK = 0
STARTPACKET_STATUS_INSUFFICIENT_PLAYERS = 1
STARTPACKET_STATUS_INVAL = -1

class StartPacket(NetPacket):
    status: int | None
    
    def __init__(self) -> None:
        super().__init__(NetPacketType.START_LOBBY, 0, 1, None)
        self.status = 0
        
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