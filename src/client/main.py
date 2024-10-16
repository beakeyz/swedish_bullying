# Import the game components
#from player import Player
import time

from twisted.protocols.socks import SOCKSv4

from .net.network import NetworkClient
from ..shared.net.packet import NetPacket, NetPacketType
from ..shared.game.game import Game

from .cli import cli

def clientThread(nc: NetworkClient):
    '''
    This boi is responsible for managing the actual game state and such things
    
    After we are connected to the server, this function will first act as a navigation tool,
    with which a user is able to connect to lobbies, disconnect from lobbies, play the game, ect.
    '''
    
    try:
        print(f"Waiting until we've connected to the server...")
        
        # Wait until we're connected
        while not nc.isConnected():
            time.sleep(0.001)
            
        print("Connected! Type \'help\' for help")
        
        # Loop as long as we're connected
        while nc.isConnected():
            cmd = input("> ")
            
            if cli.CliStep(cmd, nc) > 0:
                print("Command not recognised (type \'help\' for help)!")
    except KeyboardInterrupt and EOFError:
        return
    
def notifyThread(nc: NetworkClient):
    while not nc.isConnected():
        time.sleep(0.001)
        
    while nc.isConnected():
        cli.CliPollNotify(nc)
        
        # Sleep this thread for 50ms
        time.sleep(0.05)
        

def main() -> None:
    g = Game()

    #g.addPlayer(Player("You"))
    #g.addPlayer(Player("Bot"))

    #g.start()
    
    client = NetworkClient(g)
    
    client.connect("localhost", 8007, clientThread, notifyThread)

    pass

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass