import enum
from ..net.packet import NetPacketStream, NetPacketType

class CardType(enum.Enum):
    SPADES = 0
    HEARTS = 1
    CLUBS = 2
    DIAMONDS = 3
    
    def __str__(self) -> str:
        IDX_LIST: list[str] = [
            "Spades",
            "Hearts",
            "Clubs",
            "Diamonds"
        ]
        
        if self.value >= len(IDX_LIST):
            return "<Invalid/>"

        return IDX_LIST[self.value]

class Card(object):
    value: int
    cardType: CardType

    def __init__(self, value, cardType) -> None:
        self.value = value
        self.cardType = cardType

    def __str__(self) -> str:
        if (self.value == 15):
            return "Joker"
        
        card_val: str = {11: "J", 12: "Q", 13: "H", 14: "A"}. get(self.value, str(self.value))
        return f"{card_val} of {str(self.cardType)}"

def marshalCard(card: Card, data: bytearray) -> None:
    packedCardByte = (card.value & 0x0f) << 4
    packedCardByte |= int(card.cardType.value) & 0xf
    
    data.append(packedCardByte)
    
def unmarshalCard(data: NetPacketStream) -> Card | None:
    '''
    Tries to unmarshal a card from a netpacket stream
    
    Assumes the consume pointer is pointing to a card structure
    '''
    cardByte = data.consume()
    cardType = CardType(cardByte & 0x0f)
    cardValue = int((cardByte >> 4) & 0x0f)
    
    if cardType == None or cardValue == None:
        return None
    
    return Card(cardValue, cardType)