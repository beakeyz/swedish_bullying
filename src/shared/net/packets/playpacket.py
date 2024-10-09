from ..packet import *
from ...game.card import Card, marshalCard, unmarshalCard

class PlayPacket(NetPacket):
    cardIndices: list[int]
    
    def __init__(self, cardIndices=None) -> None:
        super().__init__(NetPacketType.PLAY_CARD, 0, 1)
        
        self.cardIndices = cardIndices
        
    def marshal(self) -> bytearray:
        data: bytearray = super().marshal()

        if not self.cardIndices or not len(self.cardIndices):
            return data
    
        # Get the length in here
        data.append(len(self.cardIndices))

        # Append the indices (Max 255)
        for c in self.cardIndices:
            data.append(min(abs(c), 255))
        
        return data
    
    def unmarshal(self, data: NetPacketStream):
        if data == None:
            return
        
        # Unmarshal the base packet
        super().unmarshal(data)
        
        # Initialize the list
        self.cardIndices = []
        
        # Grab the number of cards
        nrCards = data.consume()
        
        if not nrCards:
            return
        
        # Append all the indices
        for i in range(nrCards):
            self.cardIndices.append(data.consume())
        
class NotifyPlayPacket(NetPacket):
    cards: list[Card]
    playerId: int
    nextPlayerId: int
    
    def __init__(self, cards=None, playeId=None, nextPlayerId=None) -> None:
        super().__init__(NetPacketType.NOTIFY_PLAY_CARD, NETPACKET_FLAG_CLIENTBOUND, 1)
        
        self.cards = cards
        self.playerId = playeId
        self.nextPlayerId = nextPlayerId
        
    def marshal(self) -> bytearray:
        data: bytearray = super().marshal()
                
        data.append(self.playerId)
        data.append(self.nextPlayerId)
        data.append(len(self.cards))
        
        for c in self.cards:
            marshalCard(c, data)
        
        return data
    
    def unmarshal(self, data: NetPacketStream):
        if data == None:
            return
        
        super().unmarshal(data)
        
        # Initialize our card
        self.playerId = data.consume()
        self.nextPlayerId = data.consume()
        # Initialize the cards array
        self.cards = []
        
        # Grab the number of cards played
        nrCards = data.consume()
        
        if not nrCards:
            return

        assert nrCards <= 4, "Tried to unmarshal a NotifyPlayPacket with an invalid number of cards"
        
        # Append all cards to our list
        for i in range(nrCards):
            self.cards.append(unmarshalCard(data))