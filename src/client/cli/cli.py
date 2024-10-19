import re

from ..net.network import NetworkClient

from ...shared.net.packets import *
from ...shared.net.packet import *

from ...shared.game.game import Game
from ...shared.game.card import Card, CardType
from ...shared.game.player import GamePlayer

def __cli_help(input: str, argv: list[str], nc): 
    print("Available commands:")
    for c in __cli_commands:
        print(f" - {c}: {__cli_commands[c][1]}")
        
def __cli_exit(input: str, argv: list[str], nc: NetworkClient):
    nc.disconnect(0)

def __cli_join(input: str, argv: list[str], nc: NetworkClient):
    game: Game = nc.game
    netResponse: JoinNetPacket = None
    lobbyId: int
    
    if len(argv) != 3:
        print("Please supply all the required arguments! (lobbyID and player name)")
        return
    
    try:
        lobbyId = int(argv[1])
    except:
        print("Please supply a valid lobby ID")
        return

    # Ask server to join
    response = nc.SendPacketAndAwaitResponse(JoinNetPacket(incomming=False, lobbyId=lobbyId, playerName=argv[2]))
    
    # Check if no oof
    if response == None:
        print("Failed to join that lobby")
        return
    
    # Transform
    netResponse: JoinNetPacket = JoinNetPacket().fromPacket(response)
    
    if netResponse.playerId == JoinNetPacket.InvalidPlayerId():
        print("Failed to join that lobby =(")
        return
    
    game.SetLobbyId(lobbyId)
    
    # Add ourselves to the thing
    game.addGamePlayer(GamePlayer(argv[2], 0, nc, netResponse.playerId, lobbyId))
    
    # Register ourselves as the main player
    game.ourPlayerId = netResponse.playerId

    print(f"Success! Player {argv[2]} joined with ID {netResponse.playerId}")
    print(f"{netResponse.nrGamePlayer} players already in this lobby!")
    if netResponse.nrGamePlayer and netResponse.gamePlayers != None:
        print(f"Players: ")
        for p in netResponse.gamePlayers:
            print(f" - Name: {p.name} Id: {p.playerId}")
            
            game.addGamePlayer(GamePlayer(p.name, 0, None, p.playerId, game.currentLobbyId))


def __cli_leave(input: str, argv: list[str], nc: NetworkClient):
    nc.SendPacket(0, LeavePacket())

def __cli_create(input: str, argv: list[str], nc: NetworkClient):
    netResponse: CreateLobbyPacket = None
    lobbyId: int
    
    if len(argv) != 2:
        print("Please supply all the required arguments! (lobbyID)")
        return
    
    try:
        lobbyId = int(argv[1])
    except:
        print("Please supply a valid lobby ID")
        return
    
    response = nc.SendPacketAndAwaitResponse(CreateLobbyPacket(lobbyId=lobbyId))
    
    if response == None:
        print(f"Failed to create a lobby with lobby ID {lobbyId}!")
        return
    
    netResponse = CreateLobbyPacket().fromPacket(response)
    
    if netResponse == None or netResponse.lobbyId == CreateLobbyPacket.InvalidLobbyId():
        print(f"Failed to create lobby with ID {lobbyId}")
        return
    
    print(f"Succesfuly created lobby {lobbyId}")

def __cli_destroy(input: str, argv: list[str], nc: NetworkClient):
    pass

def __cli_start(input: str, argv: list[str], nc: NetworkClient):
    # Send a start packet =D
    status = nc.SendPacket(0, StartPacket())
    
    if status < 0:
        print(f"Failed to start the lobby!")
        return
    
    print("Succesfully started the lobby!")

__cli_commands = {
    "help": [__cli_help, "Display this info"],
    "exit": [__cli_exit, "Exits the application"],
    "join": [__cli_join, "Joins a lobby. Usage: join <lobby id> <player name>"],
    "leave": [__cli_leave, "Leaves the current lobby"],
    "create": [__cli_create, "Creates a new lobby. Usage: create <lobby id>"],
    "destroy": [__cli_destroy, "Destroys the current lobby"],
    "start": [__cli_start, "Starts the current lobby if there are enough players"],
}

def CliPollNotify(nc: NetworkClient):
    game: Game = nc.game
    notifyPacket: NetPacket = nc.PollNotifyPacket()
        
    if notifyPacket == None:
        return
    
    # Newline
    print("")
    
    if notifyPacket.type == NetPacketType.NOTIFY_JOIN_LOBBY:
        print(f"Got a join notify packet!")
        
        # Unpack the packet to find the data
        notifyPacket: NotifyJoinPacket = NotifyJoinPacket().fromPacket(notifyPacket)
        
        print(f"Player to join: name={notifyPacket.playerName}, id={notifyPacket.playerId}")
        
        # TODO: Actually add the players to the game
        game.addGamePlayer(GamePlayer(notifyPacket.playerName, 0, None, notifyPacket.playerId, game.currentLobbyId))
    elif notifyPacket.type == NetPacketType.NOTIFY_LEAVE_LOBBY:
        pass
    elif notifyPacket.type == NetPacketType.TAKE_CARDS:
        takePacket: TakePacket = TakePacket().fromPacket(notifyPacket)
        
        us: GamePlayer = game.GetPlayerById(game.ourPlayerId)
        
        # If we don't yet have any cards, these are our starting cards
        if not len(us.hand) and not len(us.closed):
            print(f"Taking starting cards...")
            
            game.started = True
            
            # Fill up our closed hand with bullshit
            # Since the server is going to keep track of our closed
            # cards and we're going to play indices anyway, there is no
            # need to put anything meeaningful here
            # 
            # oinky sploinky punch H13 (vo') for the win
            for i in range(3):
                us.takeClosedCard(card=Card(15, CardType.SPADES))

            i = 0

            
            for card in takePacket.targetCards:
                us.takeCard(card)
                
                print(f"Card ({i}): {str(card)}")
                i += 1
                
            print(f"Please select 3 cards to play open! (0-{len(takePacket.targetCards)})")
        else:
            print(f"You need to take {len(takePacket.targetCards)} card(s):")
            
            if len(takePacket.targetCards):
                for card in takePacket.targetCards:
                    us.takeCard(card)
                    print(f" - {str(card)}")
                      
            # Only if there is a valid next player supplied
            if takePacket.nextPlayerId != JoinNetPacket.InvalidPlayerId():
                nextPlayer: GamePlayer = game.GetPlayerById(takePacket.nextPlayerId)
                
                print(f"Next player is: {nextPlayer.name}")
                
                # If the packet indicates a next player, we had to take the pile, so let's clear it
                game.discardPile.cards.clear()
                    
                game.SetCurrentPlayer(takePacket.nextPlayerId)
                
    elif notifyPacket.type == NetPacketType.NOTIFY_PLAY_CARD:
        playPacket: NotifyPlayPacket = NotifyPlayPacket().fromPacket(notifyPacket)
        
        # NOTE: It's also possible for us to get notified about our own play
        us: GamePlayer = game.GetPlayerById(game.ourPlayerId)
        them: GamePlayer = game.GetPlayerById(playPacket.playerId)
        nextPlayer: GamePlayer = game.GetPlayerById(playPacket.nextPlayerId)
        
        print(f"Player {them.name} played the:")
        
        # Print all played cards
        for c in playPacket.cards:
            print(f" - {str(c)}")
        
        print(f"Next player is: {nextPlayer.name}")
        
        if playPacket.playerId == us.playerId:
            
            hand = us.getActivePlayingHand()
            indices: list[int] = []
            
            # Grab the indices of the target cards
            idx = 0
            for handCard in hand:
                for c in playPacket.cards:
                    if c.value == handCard.value and c.cardType.value == handCard.cardType.value:
                        indices.append(idx)
                        break
                idx+=1
            
            # Play these cards
            game.tryGamePlayerPlay(us, indices)
        else:
            # Add all these cards to their hand
            them.takeCards(playPacket.cards)
            
            # Play every card in their hand right now
            game.playCard(them, [x for x in range(len(them.hand))])
        
        if playPacket.nextPlayerId == game.ourPlayerId:
            game.NotifyPlayerOfTurn(us)
            
        game.SetCurrentPlayer(playPacket.nextPlayerId)
    elif notifyPacket.type == NetPacketType.NOTIFY_START_GAME:
        notifyStart: NotifyActualStartPacket = NotifyActualStartPacket(0).fromPacket(notifyPacket)
        
        us: GamePlayer = game.GetPlayerById(game.ourPlayerId)
        them: GamePlayer = game.GetPlayerById(notifyStart.startPlayerId)
        
        # Make sure we're all on the same page
        game.SetCurrentPlayer(notifyStart.startPlayerId)
        
        print(f"Game has actually started! id={notifyStart.startPlayerId} may start playing")
        
        if notifyStart.startPlayerId == game.ourPlayerId:
            print(f"It's your turn! Select a card to play!")
            print(f"Top card on the discard pile: {game.discardPile.getTopCardFmt()} ({len(game.discardPile.cards)} Cards)")
            
            if not game.checkAndDisplayGamePlayerHand(us):
                print(f"Ay! It seems like you can't play... You'll have to take the discard pile")
    elif notifyPacket.type == NetPacketType.NOTIFY_TAKE_CARDS:
        # When we get notified of a take, we need to check the next player
        notifyTake: NotifyTakePacket = NotifyTakePacket().fromPacket(notifyPacket)
        
        us: GamePlayer = game.GetPlayerById(game.ourPlayerId)
        sjaakPlayer: GamePlayer = game.GetPlayerById(notifyTake.pieneutPlayerId)
        nextPlayer: GamePlayer = game.GetPlayerById(notifyTake.nextPlayerId)
        
        print(f"{sjaakPlayer.name} has to take the discard pile! What a shame xD")
        
        print(f"Next player is: {nextPlayer.name}")
        
        # Clear this pile
        game.discardPile.cards.clear()
        
        # Set the current player to the corret value so we can play
        game.SetCurrentPlayer(notifyTake.nextPlayerId)
        
        if notifyTake.nextPlayerId == game.ourPlayerId:
            game.NotifyPlayerOfTurn(us)
        
    print("> ", end='', flush=True)

def CliStep(input: str, nc: NetworkClient) -> int:
    game: Game = nc.game
    argv: list[str] = input.split()
    func = None
    
    # Check if we're in game mode
    if game.started:
        indices = [int(s) for s in re.findall(r'\d+', input)]
        us: GamePlayer = game.GetPlayerById(game.ourPlayerId)
        
        print(f"Debug: indices={indices}, game.ourPlayerId={game.ourPlayerId}, game.currentPlayerId={game.currentPlayerId}")
        
        # Check if we're still selecting open cards
        if game.currentPlayerId == JoinNetPacket.InvalidPlayerId() and len(us.hand) == 6:
            # If this works, forward to the server
            # NOTE: This assumes the players card indices are synced 
            # between the server and client side
            if us.trySelectOpenCards(indices):
                nc.SendPacket(0, PlayPacket(indices))
        
        # Need to 'play' either when it's our turn, or when we need to select open cards
        elif game.ourPlayerId == game.currentPlayerId:
            # Send this shit
            nc.SendPacket(0, PlayPacket(indices))
        else:
            pass
        
        return 0
    else:
        try:
            func = __cli_commands[argv[0]]
            
            if func == None:
                return 1
        except:
            return 1
    
        func[0](input, argv, nc)
    
    return 0
