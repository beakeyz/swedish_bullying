# Import the game components
#from game import Game
#from player import Player

from .net.network import NetworkClient

def main() -> None:
    #g = Game()

    #g.addPlayer(Player("You"))
    #g.addPlayer(Player("Bot"))

    #g.start()
    
    client = NetworkClient()
    
    client.connect("localhost", 8007)

    pass

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass