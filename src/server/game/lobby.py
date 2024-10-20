import random

from .player import *

from ..debug.log import DebugLog, OkLog, ErrorLog, WarningLog

from ...shared.net.packet import NetPacket, NetPacketType
from ...shared.net.packets import *
from ...shared.net.netif import NetworkInterface
from ...shared.game.player import GamePlayer
from ...shared.game.game import Game


class Lobby(object):
    players: list[Player] = []
    maxPlayers: int
    nrPlayers: int
    nextPlayerId: int
    lobbyId: int
    game: Game
    started: bool

    def __init__(self, id) -> None:
        self.maxPlayers = 5
        self.nrPlayers = 0
        self.nextPlayerId = 0
        self.started = False
        self.lobbyId = id
        self.game = Game()
        
    def AddPlayer(self, pl: Player) -> int:
        if self.nrPlayers >= self.maxPlayers:
            return -1

        # Check for duplicate names
        for p in self.players:
            if pl.name == p.name:
                return -1

        self.nrPlayers += 1

        # Set the players ID
        pl.SetPlayerId(self.nextPlayerId)

        self.players.append(pl)

        # Add one
        self.nextPlayerId += 1

        return pl.id

    def RemovePlayer(self, pl: Player) -> bool:
        index: int = 0

        if not self.nrPlayers:
            return False

        for p in self.players:
            if p.name == pl.name:
                self.players.pop(index)
                self.nrPlayers -= 1

                return True

            index += 1

        # Can't find this player, sad =(
        return False

    def GetPlayerByName(self, name: str) -> Player | None:
        for p in self.players:
            if p.name == name:
                return p

        return None

    def GetPlayerById(self, id: int) -> Player | None:
        for p in self.players:
            if p.id == id:
                return p

        return None
    
    def GetPlayerByConnId(self, connId: int) -> Player | None:
        for p in self.players:
            if p.connectionId == connId:
                return p
            
        return None
    
    def start(self, netif: NetworkInterface) -> None:
        
        for p in self.players:
            # Create the new gameplayer
            gp = GamePlayer(p.name, p.connectionId, netif, p.id, self.lobbyId)
            
            # Add them to the game
            self.game.addGamePlayer(gp)
            
            # Register them in the player backend
            p.gamePlayer = gp
            
            DebugLog(f"Adding player name={p.name}, connId={p.connectionId}, playerId={p.id}, lobbyId={self.lobbyId}")

        self.game.start()
                
        self.started = True

    def HandleIncommingPacket(self, connId: int, netif: NetworkInterface, netPacket: NetPacket) -> bool:
        game: Game = self.game
        npType = netPacket.type
        playPacket: PlayPacket = None
        gamePlayer: GamePlayer = self.GetPlayerByConnId(connId).gamePlayer
        
        print(f"HandleIncommingPacket Lobby {self.lobbyId}")
        
        if npType == NetPacketType.PLAY_CARD:
            playPacket = PlayPacket().fromPacket(netPacket)
            
            # We're still collecting open cards
            if game.currentPlayerId == JoinNetPacket.InvalidPlayerId():
                if not gamePlayer.trySelectOpenCards(playPacket.cardIndices):
                    return True
                
                # Check if all players have selected their cards
                for gp in game.gamePlayers:
                    if len(gp.hand) != 3:
                        return True
                    
                # Select a random start player
                startPlayerIdx = random.randrange(0, len(game.gamePlayers))
                
                # Grab the startID
                startPlayerId = game.gamePlayers[startPlayerIdx].playerId
                
                # Set it here
                game.SetCurrentPlayer(startPlayerId)
                
                # Notify everyone of the starting player
                for gp in game.gamePlayers:
                    gp.SendPacket(NotifyActualStartPacket(startPlayerId))
            else:
                # Play succeeded, find the next player to play
                if not game.checkGamePlayerHand(gamePlayer, False):
                    # This player can't play any card, let them take the pile
                    pile = game.discardPile.cards
                    
                    # Grab the next player
                    game.NextPlayer()
                    
                    # Send a packet to make them take the cards
                    gamePlayer.SendPacket(TakePacket(game.currentPlayerId, pile))
                    
                    # Let them take the entire pile xDDDD
                    game.discardPile.takePile(gamePlayer)
                    
                    # Notify the other players of this event
                    for gp in game.gamePlayers:
                        if gp.playerId == gamePlayer.playerId:
                            continue
                        
                        # Update the clients
                        gp.SendPacket(NotifyTakePacket(gamePlayer.playerId, game.currentPlayerId))
                
                    return True

                # Grab the cards this player wants to play
                playCards = gamePlayer.getCardsFromIndices(playPacket.cardIndices)                
                
                # Try to play this card
                if playCards is None or not game.tryGamePlayerPlay(gamePlayer, playPacket.cardIndices):
                    return True
               
                if len(gamePlayer.hand) < 3:
                    cards = game.drawPile.tryTakeCards(3 - len(gamePlayer.hand))

                    # Grab these cards localy                    
                    gamePlayer.takeCards(cards)
                    
                    # Tell the player it is taking some new cards
                    gamePlayer.SendPacket(TakePacket(0xff, cards))

                # Maybe cycle to the next player                
                game.NextPlayer(game.shouldKeepGamePlayer)

                # Notify all other players of the play
                for gp in game.gamePlayers:
                    ErrorLog(f"Sending play notify to {gp.name}")
                    # Update the clients
                    gp.SendPacket(NotifyPlayPacket(playCards, gamePlayer.playerId, game.currentPlayerId))
                

        return True


class LobbyManager(object):
    lobbies: dict[int, Lobby] = {}

    def __init__(self) -> None:
        pass

    def AddLobby(self, lobbyId: int) -> bool:
        if self.lobbies.get(lobbyId) != None:
            return False

        self.lobbies[lobbyId] = Lobby(lobbyId)

        return True

    def RemoveLobby(self, lobbyId: int) -> bool:
        if self.lobbies.get(lobbyId) == None:
            return False

        self.lobbies.pop(lobbyId)

        return True

    def GetLobby(self, lobbyId: int) -> Lobby | None:
        return self.lobbies.get(lobbyId)

    def GetLobbyId(self, lobby: Lobby) -> int | None:
        for id in self.lobbies:
            if self.lobbies[id] == lobby:
                return id

        return None

    def GetLobbyAndPlayerForConnId(self, connId: int) -> tuple[Lobby, Player] | None:
        for lobbyId in self.lobbies:
            lobby: Lobby = self.lobbies[lobbyId]

            for p in lobby.players:
                if p.connectionId == connId:
                    return (lobby, p)

        return None

    def GetPlayerByName(self, playerName: str) -> Player | None:
        for lobbyId in self.lobbies:
            lobby: Lobby = self.lobbies[lobbyId]

            p: Player = lobby.GetPlayerByName(playerName)

            if p != None:
                return p

        return None

    def IsPlayerInLobby(self, playerName: str) -> bool:
        return self.GetPlayerByName(playerName) != None

    def HandleIncommingPacket(self, connId: int, cm: NetworkInterface, netPacket: NetPacket) -> bool:
        '''
        Parse the packet to figure out which lobby this packet is meant for
        '''
        packetType: NetPacketType = netPacket.type

        if packetType == NetPacketType.JOIN_LOBBY:
            joinPacket = JoinNetPacket().fromPacket(netPacket)

            DebugLog(f"Player {joinPacket.playerName} is trying to join lobby {joinPacket.lobbyId}")

            # Check if this connection has alread joined a lobby
            if self.GetLobbyAndPlayerForConnId(connId) != None:
                cm.SendPacket(connId, JoinNetPacket(
                    incomming=True, playerId=JoinNetPacket.InvalidPlayerId(), lobbyId=CreateLobbyPacket.InvalidLobbyId()))
                return False

            gamePlayerList: list[GamePlayer] | None = None
            playerId: int = JoinNetPacket.InvalidPlayerId()
            lobby: Lobby = self.GetLobby(joinPacket.lobbyId)

            # Add the player to the lobby if it exists
            if lobby != None:
                gamePlayerList = [GamePlayer(p.name, p.connectionId, None, p.id, joinPacket.lobbyId) for p in lobby.players]

                playerId = lobby.AddPlayer(
                    Player(joinPacket.playerName, connId))

                DebugLog(f"Player ID result: {playerId}")

                if playerId < 0:
                    playerId = JoinNetPacket.InvalidPlayerId()
                else:
                    # Notify other players of this join event
                    for playerInLobby in lobby.players:
                        # Make sure to skip the player that just joined, they obviously dont
                        # need to be notified that a players has joined ._.
                        if playerInLobby.id != playerId:
                            cm.SendPacket(playerInLobby.connectionId, NotifyJoinPacket(
                                joinPacket.playerName, playerId))

            # Send the response packet to the client
            cm.SendPacket(connId, JoinNetPacket(incomming=True, playerId=playerId, lobbyId=joinPacket.lobbyId, gamePlayers=gamePlayerList))
        elif packetType == NetPacketType.LEAVE_LOBBY:
            result: tuple[Lobby, Player] = self.GetLobbyAndPlayerForConnId(
                connId)

            if result == None:
                return False

            id = self.GetLobbyId(result[0])

            if id == None:
                id = -1

            DebugLog(f"Player {result[1].name} is trying to leave lobby {id}")

            # Remove the player from it's lobby
            result[0].RemovePlayer(result[1])
        elif packetType == NetPacketType.CREATE_LOBBY:
            lobbyId: int = CreateLobbyPacket.InvalidLobbyId()
            createPacket: CreateLobbyPacket = CreateLobbyPacket().fromPacket(netPacket)

            print(f"Connection {connId} is trying to create a lobby with ID {createPacket.lobbyId}")

            # Try to create a lobby with this ID
            if createPacket != None and self.AddLobby(createPacket.lobbyId):
                lobbyId = createPacket.lobbyId

                print(f"Created a lobby with ID {lobbyId}")

            # Send a response packet
            cm.SendPacket(connId, CreateLobbyPacket(
                clientbound=True, lobbyId=lobbyId))
            
        elif packetType == NetPacketType.START_LOBBY:
            lobby: Lobby = None
            player: Player = None
            startPacket: StartPacket = StartPacket()
            lpSet = self.GetLobbyAndPlayerForConnId(connId)
            
            startPacket.status = STARTPACKET_STATUS_INVAL
            
            if lpSet != None: 
                lobby = lpSet[0]
                player = lpSet[1]
                
                if lobby.nrPlayers < 2:
                    startPacket.status = STARTPACKET_STATUS_INSUFFICIENT_PLAYERS  
                elif player == None:
                    startPacket.status = STARTPACKET_STATUS_INVAL
                else:
                    startPacket.status = STARTPACKET_STATUS_OK
                    
                    lobby.start(cm)                    
        else:
            lpSet = self.GetLobbyAndPlayerForConnId(connId)
            
            if lpSet == None or lpSet[0] == None:
                return True
            
            # Pass the packet to the lobby
            return lpSet[0].HandleIncommingPacket(connId, cm, netPacket)
        return True
