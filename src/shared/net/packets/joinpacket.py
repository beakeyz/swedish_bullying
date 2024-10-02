from shared.net.packet import NetPacket, NETPACKET_FLAG_INCOMMING

class JoinNetPacket(NetPacket):
    lobbyId: int
    playerId: int
    playerName: str

    def __init__(self, data) -> None:
        super().__init__(data)
        
        if self.hasFlags(NETPACKET_FLAG_INCOMMING):
            if len(data) == 5:
                self.playerId = data[4]
        else:
            if len(data) >= 6:
                self.lobbyId = (data[4] << 8) | data[5]
                
                # TODO: Unmarshal playername
                self.playerName = "TODO: parse playername"
    
    def marshal(self) -> bytearray:
        # Let NetPacket do the default header
        ret: bytearray = super().marshal()

        if self.hasFlags(NETPACKET_FLAG_INCOMMING):
            ret += self.playerId & 0xff
        else:
            ret += (self.lobbyId >> 8) & 0xff
            ret += (self.lobbyId) & 0xff
            
            # Simply append the chars to the stream
            for c in self.playerName:
                ret += c
        
        return ret