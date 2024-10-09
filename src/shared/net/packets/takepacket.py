from ..packet import *
from ...game import Card, marshalCard, unmarshalCard

class TakePacket(NetPacket):
    targetCards: list[Card]
    def __init__(self, clientbound=False, cards=None):
        super().__init__(NetPacketType.TAKE_CARDS, NETPACKET_FLAG_CLIENTBOUND if clientbound else 0, 1, None)
        
        self.targetCards = cards
        
    def marshal(self) -> bytearray:
        data: bytearray = super().marshal()
        
        if not len(self.targetCards):
            return data
        
        if self.isClientBound():
            data.append(len(self.targetCards))
            
            for targetCard in self.targetCards:
                marshalCard(targetCard, data)
                
        else:
            if len(self.targetCards) == 1:
                data.append(1)
                data.append(self.targetCards[0])
        
        return data
    
    def unmarshal(self, data: NetPacketStream):
        if data == None:
            return
        
        super().unmarshal(data)
        
        cardCount: int = data.consume()
        
        for i in range(cardCount):
            self.targetCards.append(unmarshalCard(data))