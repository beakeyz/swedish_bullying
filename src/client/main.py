import re
import enum
import random

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
    
    def removeCard(self, c: Card) -> bool:
        if c in self.hand:
            self.hand.remove(c)
            return True
        
        if c in self.open:
            self.open.remove(c)
            return True
        
        if c in self.closed(c):
            self.closed.remove(c)
            return True
        
        return False

   
class Pile(object):
    cards: list[Card] = []

    def __init__(self, cards) -> None:
        self.cards = cards

    # Lets a player take an entire pile of cards
    def takePile(self, p: Player) -> None:
        p.takeCards(self.cards)
        self.cards.clear()

    def mergePiles(self, p) -> None:
        self.cards.extend(p.cards)
        p.cards.clear()

    # Lets a player take the top card from a pile
    def takeCard(self, p: Player) -> None:
        p.takeCard(self.cards.pop(0))

    def takeClosedCard(self, p: Player) -> None:
        p.takeClosedCard(self.cards.pop(0))

    def takeOpenCard(self, p: Player) -> None:
        p.takeOpenCard(self.cards.pop(0))

    def hasCards(self) -> bool:
        return len(self.cards) > 0

    def shuffle(self) -> None:
        new_list: list[Card] = []
        # Generate a range of indices
        ran: range = range(len(self.cards))

        for i in ran:
            r_idx = random.randint(0, len(self.cards)-1)

            # Take a random card from the current list
            card: Card = self.cards.pop(r_idx)

            # Place back this card in the new list
            new_list.append(card)
        
        # Replace the list
        self.cards = new_list

    def getTopCard(self) -> Card:
        return self.cards[0]

    def getTopCardFmt(self) -> str:
        ret: str = ""

        if len(self.cards) == 0:
            return "No card on this pile yet"

        for i in range(min(4, len(self.cards))):
            ret += str(self.cards[i])

            if self.cards[i].value != 3:
                break

            ret += " => "
        
        return ret

     # Checks if this card can be played on a certain valued card
    def canPlay(self, card: Card, index: int = 0) -> bool:
        # If there are no cards on this pile, you can always play
        if len(self.cards) == 0:
            return True
        
        # Grab the value of the target card
        value = self.cards[index].value

        # These special case cards or cards of the same value are always playable
        if card.value == 2 or card.value == 3 or card.value == 10 or card.value == 15 or card.value == value:
            return True
        
        # You can always play on top of jokers or twos
        if value == 2 or value == 15:
            return True
        
        # Threes are glass, so we'll need to check the next card in the pile
        if value == 3:
            return self.canPlay(card, index+1)
        
        # This card has to be lower than a seven, in order for it to be playable in this case
        if value == 7:
            return card.value < value
        else:
            return card.value > value
        
    
    # Selects a few cards to play
    def playCards(self, p: Player, indices: list[int]) -> bool:
        card_value: int
        ret: list[Card] = []
        cards: tuple[list[Card], int] = p.getPlayableCards()

        # Check if we supplied the correct number of cards to play
        if len(indices) > cards[1]:
            return False

        try:
            # Grab the value of the first card
            card_value = cards[0][indices[0]].value

            # Check if we can play the first card
            if not self.canPlay(cards[0][indices[0]]):
                return False

            # If there is only one card specified, we can just take this one
            if len(indices) == 1:
                card = cards[0][indices[0]]

                # Add to the result set
                ret.append(card)

                # Also remove it from our hand
                p.removeCard(card)
            else:
                # Match all cards agains this one
                for idx in indices:
                    card = cards[0][idx]

                    # Value mismatch, play fails
                    if card.value != card_value:
                        return False
                    
                    # Add this boi to the cards-to-play-list
                    ret.append(card)

                # Remove all these cards from the players hand when we know these cards are playable
                for r in ret:
                    p.removeCard(r)

        except ValueError and IndexError:
            return False
        
        # Insert the cards at the front
        for i in ret:
            self.cards.insert(0, i)

        return True

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

        # Play the game
        while True:
            self.shouldCyclePlayer = True

            canPlay: bool = False
            currentPlayer: Player = self.players[cPlayerIdx]

            print(f"\nPlayer: {currentPlayer.name} is playing (Open hand: {currentPlayer.open[0]}, {currentPlayer.open[1]}, {currentPlayer.open[2]})")
            print(f"Cards left on the draw pile: {len(self.drawPile.cards)}")
            print(f"Top card on the pile: {self.discardPile.getTopCardFmt()} ({len(self.discardPile.cards)} Cards)")
            print("Hand:")

            for i in range(len(currentPlayer.getActivePlayingHand())):
                currentCard: Card = currentPlayer.getActivePlayingHand()[i] if len(currentPlayer.open) else None
                
                if currentCard != None:
                    print(f" ({i}): {currentCard}")

                    if not canPlay:
                        canPlay = self.discardPile.canPlay(currentCard)
                else:
                    print(f" ({i}) ???")

            if not canPlay:
                print("You can't play! You need to take the pile =(")

                self.discardPile.takePile(currentPlayer)
            else:
                while True:
                    try:
                        play = input(f"\nEnter the index/indices of the card(s) you want to play (0 - {len(currentPlayer.getActivePlayingHand())-1}): ")

                        # Parse the input
                        indices: list[int] = [int(s) for s in re.findall(r'\d+', play)]

                        print(indices)

                        # Try to play this input
                        if self.playCard(currentPlayer, indices):
                            break
                    except ValueError and IndexError:
                        pass

                # Fill your hand back until there are 3 in your hand
                while len(currentPlayer.hand) < 3 and self.drawPile.hasCards():
                    self.drawPile.takeCard(currentPlayer)
            
            if self.shouldCyclePlayer:
                # Go next player
                cPlayerIdx += 1
                cPlayerIdx %= len(self.players)
        
            pass


def main() -> None:
    g = Game()

    g.addPlayer(Player("You"))
    g.addPlayer(Player("Bot"))

    g.start()

    pass

if __name__ == "__main__":
    main()