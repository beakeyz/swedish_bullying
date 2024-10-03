import random

from ..shared.game.card import Card
from .player import Player

class Pile(object):
    cards: list[Card] = []

    def __init__(self, cards) -> None:
        self.cards = cards

    # Lets a player take an entire pile of cards
    def takePile(self, p: Player) -> None:
        print(f"{p.name} has to take the pile!")
        
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
        
        # If we're trying to check past the bottom of the card pile,
        # there is something like a three all alone here, so we can
        # always play =)
        if index >= len(self.cards):
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
