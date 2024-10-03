from ..packet import *

class CreateLobbyPacket(NetPacket):
    lobbyId: int
    
    def __init__(self, clientbound=False, lobbyId=None) -> None:
        super().__init__(NetPacketType.CREATE_LOBBY, NETPACKET_FLAG_CLIENTBOUND if clientbound else 0, 1, None)
        
        self.lobbyId = lobbyId
        
    def InvalidLobbyId() -> int:
        return 0xffff
        
    def marshal(self) -> bytearray:
        data: bytearray = super().marshal()
        
        data.append((self.lobbyId >> 8) & 0xff)
        data.append(self.lobbyId & 0xff)
        
        return data
    
    def unmarshal(self, data: bytes):
        if data == None:
            return
        
        super().unmarshal(data)
        
        # Make sure we have enough data here xD
        if len(data) != 6:
            return
        
        self.lobbyId = (data[4] << 8) | data[5]