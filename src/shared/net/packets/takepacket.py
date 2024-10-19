from ...game.card import Card, marshalCard, unmarshalCard
from ..packet import NetPacket, NetPacketType, NetPacketStream,NETPACKET_FLAG_CLIENTBOUND

class TakePacket(NetPacket):
    targetCards: list[Card] = []
    nextPlayerId: int

    def __init__(self, nextPlayerId=0xff, cards=[]):
        super().__init__(NetPacketType.TAKE_CARDS, NETPACKET_FLAG_CLIENTBOUND, 1, None)
        
        self.targetCards = cards
        self.nextPlayerId = nextPlayerId
        
    def marshal(self) -> bytearray:
        data: bytearray = super().marshal()
        
        data.append(self.nextPlayerId)
        data.append(len(self.targetCards))
        
        for targetCard in self.targetCards:
            marshalCard(targetCard, data)
        
        return data
    
    def unmarshal(self, data: NetPacketStream):
        if data == None:
            return
        
        super().unmarshal(data)
        
        # We need to take one extra byte for the next player ID if this is a clientbound packet
        self.nextPlayerId = data.consume()

        self.targetCards = []
        
        # Try to grab a card count
        cardCount: int = data.consume()

        # No cards to take lmao
        if not cardCount:
            return        
        
        for i in range(cardCount):
            self.targetCards.append(unmarshalCard(data))
            
class NotifyTakePacket(NetPacket):
    pieneutPlayerId: int
    nextPlayerId: int

    def __init__(self, pieneut=0xff, nextPlayer=0xff) -> None:
        super().__init__(NetPacketType.NOTIFY_TAKE_CARDS, NETPACKET_FLAG_CLIENTBOUND, 1)
        
        self.pieneutPlayerId = pieneut
        self.nextPlayerId = nextPlayer
        
    def marshal(self) -> bytearray:
        data: bytearray = super().marshal()
        
        data.append(self.pieneutPlayerId)
        data.append(self.nextPlayerId)
        
        return data
    
    def unmarshal(self, data: NetPacketStream):
        if not data:
            return
        
        super().unmarshal(data)
        
        self.pieneutPlayerId = data.consume()
        self.nextPlayerId = data.consume()
    
