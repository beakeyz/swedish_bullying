import re

from card import Card, CardType
from player import Player
from pile import Pile

class Game(object):
    discardPile: Pile
    drawPile: Pile
    boomPile: Pile

    shouldCyclePlayer: bool
    started: bool
    players: list[Player] = []

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

    def addPlayer(self, p: Player) -> bool:
        if p in self.players or self.started:
            return False
        
        self.players.append(p)

    def dealCards(self) -> None:
        for player in self.players:
            # Let the players take 3 open, 3 closed and 3 hand cards
            for i in range(3):
                self.drawPile.takeClosedCard(player)
                self.drawPile.takeOpenCard(player)
                self.drawPile.takeCard(player)

    def doBoom(self) -> bool:

        # Move the discard pile to the boom pile
        self.boomPile.mergePiles(self.discardPile)

        self.shouldCyclePlayer = False
        return True

    def playCard(self, p: Player, indices: list[int]) -> bool:
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
 
    # Checks the hand of a current player in the game to see if they 
    # are able to play, or if they need to take the discard pile
    def checkAndDisplayPlayerHand(self, p: Player) -> bool:
        canPlay: bool = False
        
        # Print the correct type of hand we're playing
        print("Hand:" if p.isPlayingFromHand() else "Open hand: " if p.isPlayingFromOpenHand() else "Closed hand: ")

        # Loop over all the cards in the active playing hand to check and display them
        for i in range(len(p.getActivePlayingHand())):
            currentCard: Card = p.getActivePlayingHand()[i] if len(p.open) else None
            
            if currentCard != None:
                print(f" ({i}): {currentCard}")

                if not canPlay:
                    canPlay = self.discardPile.canPlay(currentCard)
            else:
                # Just assume we can play here xD
                canPlay = True
                print(f" ({i}) ???")
               
        # Epic newline 
        print("")
        
        return canPlay
    
    def tryPlayerPlay(self, p: Player, playInput: str) -> bool:
        # Parse the input
        indices: list[int] = [int(s) for s in re.findall(r'\d+', playInput)]
        
        # When the player has an empty hand, force them to play one card at a time
        if not p.isPlayingFromHand() and len(indices) > 1:
            return False
        
        # If the player is playing from their closed hand, and the play fails, they need to take the pile =/
        if p.isPlayingFromClosedHand() and not self.playCard(p, indices):
            # Let the player pick up the discard pile
            self.discardPile.takePile(p)
            
            return True
        
        # Try to play this input
        if self.playCard(p, indices):
            return True
        
        return False
    
    def end(self) -> None:
        self.started = False
        
    def start(self) -> None:
        cPlayerIdx: int = 0

        if len(self.players) <= 1:
            return;
    
        self.started = True
        self.shouldCyclePlayer = True

        # Shuffle the deck
        self.drawPile.shuffle()

        # Deal out the cards
        self.dealCards()

        # Shuffle again to be sure
        self.drawPile.shuffle()
        
        self.boomPile.mergePiles(self.drawPile)

        # Play the game
        while True:
            self.shouldCyclePlayer = True

            canPlay: bool = False
            currentPlayer: Player = self.players[cPlayerIdx]

            print(f"\nPlayer: {currentPlayer.name} is playing (Open hand: {currentPlayer.getOpenHandFmt()})")
            print(f"Cards left on the draw pile: {len(self.drawPile.cards)}")
            print(f"Top card on the pile: {self.discardPile.getTopCardFmt()} ({len(self.discardPile.cards)} Cards)")
            
            # Check the player hand
            canPlay = self.checkAndDisplayPlayerHand(currentPlayer)

            if not canPlay:
                self.discardPile.takePile(currentPlayer)
            else:
                while True:
                    try:
                        play = input(f"Enter the index/indices of the card(s) you want to play (0 - {len(currentPlayer.getActivePlayingHand())-1}): ")

                        if self.tryPlayerPlay(currentPlayer, play):
                            break
                        
                    except ValueError and IndexError:
                        print("Please supply a valid index!")

                if currentPlayer.hasWon():
                    print(f"{currentPlayer.name} has won! ayyy")
                    return self.end()

                # Fill your hand back until there are 3 in your hand
                while len(currentPlayer.hand) < 3 and self.drawPile.hasCards():
                    self.drawPile.takeCard(currentPlayer)
            
            if self.shouldCyclePlayer:
                # Go next player
                cPlayerIdx += 1
                cPlayerIdx %= len(self.players)
