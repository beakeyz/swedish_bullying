# Import the game components
from game import Game
from player import Player

def main() -> None:
    g = Game()

    g.addPlayer(Player("You"))
    g.addPlayer(Player("Bot"))

    g.start()

    pass

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass