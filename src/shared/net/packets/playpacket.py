from ..packet import *
from ...game import Card

class PlayPacket(NetPacket):
    cardIdx: Card
    
    def __init__(self, cardIdx=None) -> None:
        super().__init__(NetPacketType.PLAY_CARD, 0, 1, 0)
        
        self.cardIdx = cardIdx
        
    def marshal(self) -> bytearray:
        data: bytearray = super().marshal()
        
        data.append(self.cardIdx)
        
        return data
    
    def unmarshal(self, data: bytes):
        if data == None:
            return
        
        super().unmarshal(data)
        
        # Make sure the length is correct
        if len(data) != 5:
            return
        
        # Initialize our card
        self.cardIdx = data[4]
        
class NotifyPlayPacket(NetPacket):
    card: Card
    playerId: int
    nextPlayerId: int
    
    def __init__(self, card=None, playeId=None, nextPlayerId=None) -> None:
        super().__init__(NetPacketType.PLAY_CARD, NETPACKET_FLAG_CLIENTBOUND, 1, 0)
        
        self.card = card
        self.playerId = playeId
        self.nextPlayerId = nextPlayerId
        
    def marshal(self) -> bytearray:
        data: bytearray = super().marshal()
        
        data.append(int(self.card.type) & 0xff)
        data.append(self.card.value & 0xff)
        data.append(self.playerId)
        data.append(self.nextPlayerId)
        
        return data
    
    def unmarshal(self, data: bytes):
        if data == None:
            return
        
        super().unmarshal(data)
        
        # Make sure the length is correct
        if len(data) != 8:
            return
        
        # Initialize our card
        self.card = Card(data[5], data[4])
        self.playerId = data[6]
        self.nextPlayerId = data[7]