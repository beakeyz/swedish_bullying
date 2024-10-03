from ..shared.game import Card

class Player(object):
    name: str
    hand: list[Card]
    closed: list[Card]
    open: list[Card]

    def __init__(self, name) -> None:
        self.name = name
        self.hand = []
        self.closed = []
        self.open = []

    def takeClosedCard(self, card: Card) -> None:
        self.closed.append(card)

    def takeOpenCard(self, card: Card) -> None:
        self.open.append(card)

    # Let the player take a single card
    def takeCard(self, card: Card) -> None:
        self.hand.append(card)
    
    # Let the player take a whole bunch of cards
    def takeCards(self, cards: list[Card]) -> None:
        self.hand.extend(cards)

    def getActivePlayingHand(self) -> list[Card]:
        if len(self.hand) != 0:
            return self.hand
        elif len(self.open) != 0:
            return self.open
        
        return self.closed

    def getPlayableCards(self) -> tuple[list[Card], int]:
        if len(self.hand) != 0:
            return self.hand, 4
        elif len(self.open) != 0:
            return self.open, 1
        
        return self.closed, 1
    
    def getOpenHandFmt(self) -> str:
        ret: str = ""
        
        for openCardIdx in range(len(self.open)):
            ret += f"{self.open[openCardIdx]}"
            if openCardIdx != len(self.open)-1:
                ret += ", "
        
        return ret        
    
    def removeCard(self, c: Card) -> bool:
        if c in self.hand:
            self.hand.remove(c)
            return True
        
        if c in self.open:
            self.open.remove(c)
            return True
        
        if c in self.closed:
            self.closed.remove(c)
            return True
        
        return False
    
    def isPlayingFromHand(self) -> bool:
        return len(self.hand) > 0
    
    def isPlayingFromOpenHand(self) -> bool:
        return len(self.hand) == 0 and len(self.open) > 0
    
    def isPlayingFromClosedHand(self) -> bool:
        return not len(self.hand) == 0 and len(self.open) == 0 and len(self.closed) >= 0
    
    def hasWon(self) -> bool:
        return len(self.hand) == 0 and len(self.closed) == 0 and len(self.open) == 0
  