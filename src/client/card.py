import enum

class CardType(enum.Enum):
    SPADES = "Spades"
    HEARTS = "Hearts"
    CLUBS = "Clubs"
    DIAMONDS = "Diamonds"

class Card(object):
    value: int
    type: CardType

    def __init__(self, value, type) -> None:
        self.value = value
        self.type = type

    def __str__(self) -> str:
        if (self.value == 15):
            return "Joker"
        
        card_val: str = {11: "J", 12: "Q", 13: "H", 14: "A"}. get(self.value, str(self.value))
        return f"{card_val} of {self.type.value}"
