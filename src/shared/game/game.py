import re

from .card import Card, CardType
from .player import GamePlayer
from .pile import Pile

from ..net.packets import TakePacket, CreateLobbyPacket, JoinNetPacket

class Game(object):
    discardPile: Pile
    drawPile: Pile
    boomPile: Pile

    started: bool
    shouldKeepGamePlayer: bool
    gamePlayers: list[GamePlayer] = []
    
    currentLobbyId: int
    ourPlayerId: int
    currentPlayerId: int

    def __generateCards(self) -> Pile:
        cards: list[Card] = []
        for type in CardType:
            # Generate the total card pile from 2 to 14 (H)
            for i in range(1, 14):
                cards.append(Card(i+1, type))

        # Why are the jokers of this type? Idk
        cards.append(Card(15, CardType.SPADES))
        cards.append(Card(15, CardType.CLUBS))

        return Pile(cards)

    def __init__(self) -> None:
        # Start with the take pile having all the cards
        self.drawPile = self.__generateCards()
        # Both these piles are empty when the game starts
        self.discardPile = Pile([])
        self.boomPile = Pile([])
        self.started = False
        self.currentLobbyId = CreateLobbyPacket.InvalidLobbyId()
        self.currentPlayerId = JoinNetPacket.InvalidPlayerId()
        
    def SetLobbyId(self, lobbyId: int) -> int:
        self.currentLobbyId = lobbyId
        
    def SetCurrentPlayer(self, pId: int) -> None:
        self.currentPlayerId = pId

    def addGamePlayer(self, p: GamePlayer) -> bool:
        if p in self.gamePlayers or self.started:
            return False
        
        self.gamePlayers.append(p)
        
    def GetPlayerById(self, pId: int, grabNext: bool=False) -> GamePlayer | None:
        idx = 0
        for p in self.gamePlayers:
            if p.playerId == pId:
                idx = ((idx + 1) % len(self.gamePlayers)) if grabNext else idx

                # Grab the target player
                return self.gamePlayers[idx]
            
            idx += 1
            
        return None
    
    def NextPlayer(self, replay: bool = False) -> GamePlayer | None:
        self.shouldKeepGamePlayer = False
        
        if replay:
            return self.GetPlayerById(self.currentPlayerId)
        
        # Grab the next fucker
        next: GamePlayer = self.GetPlayerById(self.currentPlayerId, grabNext=True)
        
        print(f"({self.GetPlayerById(self.currentPlayerId).name}) -> ({next.name})")
        
        # Check if we didn't fuck ourselves
        if next:
            self.currentPlayerId = next.playerId
            
        return next
    
    def NotifyPlayerOfTurn(self, player: GamePlayer) -> None:
        print(f"It's your turn! Select a card to play!")
        print(f"Top card on the discard pile: {self.discardPile.getTopCardFmt()} ({len(self.discardPile.cards)} Cards)")
        
        if not self.checkAndDisplayGamePlayerHand(player):
            print(f"Ay! It seems like you can't play... You'll have to take the discard pile")

    def dealCards(self) -> None:
        '''
        We're going to deal 3 closed cards and 6 open cards. All players then need to select three cards
        to present as their open cards
        '''
        for gamePlayer in self.gamePlayers:
            # Let the GamePlayers take 3 open, 3 closed and 3 hand cards
            for i in range(3):
                self.drawPile.takeClosedCard(gamePlayer)
                
            for i in range(6):
                self.drawPile.takeCard(gamePlayer)
                
            print("Taking...")
                
            # Tell the client to take these cards
            gamePlayer.SendPacket(TakePacket(True, 0xff, gamePlayer.hand))

    def doBoom(self) -> bool:

        # Move the discard pile to the boom pile
        self.boomPile.mergePiles(self.discardPile)

        self.shouldKeepGamePlayer = True
        return True

    def playCard(self, p: GamePlayer, indices: list[int]) -> bool:
        if not self.discardPile.playCards(p, indices):
            return False
        
        # If the top card is a ten, we can move the discard pile
        if self.discardPile.getTopCard().value == 10:
            return self.doBoom()

        if len(self.discardPile.cards) < 4:
            return True

        topValue: int = self.discardPile.cards[0].value

        for i in range(1, 4):
            if self.discardPile.cards[i].value != topValue:
                return True

        return self.doBoom()
 
    def checkGamePlayerHand(self, p: GamePlayer, display: bool) -> bool:
        canPlay: bool = False
        
        # Print the correct type of hand we're playing
        if display:
            print("Hand:" if p.isPlayingFromHand() else "Open hand: " if p.isPlayingFromOpenHand() else "Closed hand: ")

        # Loop over all the cards in the active playing hand to check and display them
        for i in range(len(p.getActivePlayingHand())):
            currentCard: Card = p.getActivePlayingHand()[i] if not p.isPlayingFromClosedHand() else None
            
            if currentCard != None:
                if display:
                    print(f" ({i}): {currentCard}")

                if not canPlay:
                    canPlay = self.discardPile.canPlay(currentCard)
            else:
                # Just assume we can play here xD
                canPlay = True
                
                if display:
                    print(f" ({i}) ???")
              
        if display: 
            # Epic newline 
            print("")
        
        return canPlay
 
    # Checks the hand of a current GamePlayer in the game to see if they 
    # are able to play, or if they need to take the discard pile
    def checkAndDisplayGamePlayerHand(self, p: GamePlayer) -> bool:
        return self.checkGamePlayerHand(p, True)
    
    def tryGamePlayerPlay(self, p: GamePlayer, indices: list[int]) -> bool:
        # When the GamePlayer has an empty hand, force them to play one card at a time
        if not p.isPlayingFromHand() and len(indices) > 1:
            return False
        
        # If the GamePlayer is playing from their closed hand, and the play fails, they need to take the pile =/
        if p.isPlayingFromClosedHand() and not self.playCard(p, indices):
            # Let the GamePlayer pick up the discard pile
            self.discardPile.takePile(p)
            
            return True
        
        # Try to play this input
        if self.playCard(p, indices):
            return True
        
        return False
    
    def end(self) -> None:
        self.started = False
        
    def start(self) -> None:
        if len(self.gamePlayers) <= 1:
            return;
    
        self.started = True
        self.shouldKeepGamePlayer = False

        # Shuffle the deck
        self.drawPile.shuffle()

        # Deal out the cards
        self.dealCards()

        # Shuffle again to be sure
        self.drawPile.shuffle()
                
    def tick(self) -> None:
        '''
        One game tick
        '''
        pass
