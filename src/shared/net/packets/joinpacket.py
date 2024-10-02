from ..packet import NetPacket, NetPacketType, NETPACKET_FLAG_INCOMMING, NETPACKET_FLAG_EXPECT_RESP

class JoinNetPacket(NetPacket):
    lobbyId: int
    playerId: int
    playerName: str

    def __init__(self, incomming=False, lobbyId=None, playerId=None, playerName=None, data=None) -> None:
        super().__init__(type=NetPacketType.JOIN_LOBBY, flags=(NETPACKET_FLAG_INCOMMING if incomming else 0) | NETPACKET_FLAG_EXPECT_RESP, version=1, data=data)
        
        self.lobbyId = lobbyId
        self.playerId = playerId
        self.playerName = playerName
        
    def unmarshal(self, data: bytes):
        if data == None:
            return
        
        super().unmarshal(data)
        
        if self.hasFlags(NETPACKET_FLAG_INCOMMING):
            if len(data) == 5:
                self.playerId = data[4]
        else:
            if len(data) >= 6:
                self.lobbyId = (data[4] << 8) | data[5]
                
                self.playerName = ""
                
                for i in range(len(data) - 6):
                    self.playerName += chr(data[6 + i])

    
    def marshal(self) -> bytearray:
        # Let NetPacket do the default header
        ret: bytearray = super().marshal()

        if self.hasFlags(NETPACKET_FLAG_INCOMMING):
            ret.append(self.playerId & 0xff)
        else:
            ret.append((self.lobbyId >> 8) & 0xff)
            ret.append((self.lobbyId) & 0xff)
            
            # Simply append the chars to the stream
            for c in self.playerName:
                ret.append(ord(c))
        
        return ret