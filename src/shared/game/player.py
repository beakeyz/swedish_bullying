from .card import Card

from ..net.netif import NetworkInterface
from ..net.packet import NetPacket

class GamePlayer(object):
    name: str
    netif: NetworkInterface
    connId: int
    playerId: int
    lobbyId: int
    hand: list[Card]
    closed: list[Card]
    open: list[Card]

    def __init__(self, name, connId, netif, playerId, lobbyId) -> None:
        self.name = name
        self.netif = netif
        self.playerId = playerId
        self.lobbyId = lobbyId
        self.connId = connId
        self.hand = []
        self.closed = []
        self.open = []
        
    def SendPacket(self, packet: NetPacket) -> int:
        if not self.netif:
            return -1
        
        return self.netif.SendPacket(self.connId, packet)

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
    
    def trySelectOpenCards(self, indices: list[int]) -> bool:
        # This player already has 3 open cards, don't do shit
        if len(self.open):
            return False
        
        # Invalid input
        if len(indices) != 3:
            return False
        
        # Check for invalid indices
        for cIdx in indices:
            if cIdx >= 6:
                return False
            
        newOpen = []
        newHand = []
    
        # Divide the cards over the two hands
        for i in range(len(self.hand)):
            if not i in indices:
                newHand.append(self.hand[i])
            else:
                newOpen.append(self.hand[i])
        
        # Set the new lists
        self.open = newOpen
        self.hand = newHand
        
        return True
            
    def getCardsFromIndices(self, indices: list[int]) -> list[Card] | None:
        cards = []
        
        for i in indices:
            try:
                cards.append(self.getActivePlayingHand()[i])
            except:
                return None
            
        return cards
    
    def isPlayingFromHand(self) -> bool:
        return len(self.hand) > 0
    
    def isPlayingFromOpenHand(self) -> bool:
        return len(self.hand) == 0 and len(self.open) > 0
    
    def isPlayingFromClosedHand(self) -> bool:
        return not len(self.hand) == 0 and len(self.open) == 0 and len(self.closed) >= 0
    
    def hasWon(self) -> bool:
        return len(self.hand) == 0 and len(self.closed) == 0 and len(self.open) == 0
  