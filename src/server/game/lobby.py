from . import player

from ..debug.log import DebugLog

from ...shared.net.packet import NetPacket, NetPacketType
from ...shared.net.packets import *
from ...shared.net.netif import NetworkInterface


class Lobby(object):
    players: list[player.Player] = []
    maxPlayers: int
    nrPlayers: int
    nextPlayerId: int

    def __init__(self) -> None:
        self.maxPlayers = 5
        self.nrPlayers = 0
        self.nextPlayerId = 0
    
    def AddPlayer(self, pl: player.Player) -> int:
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
    
    def RemovePlayer(self, pl: player.Player) -> bool:
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
    
    def GetPlayerByName(self, name: str) -> player.Player | None:
        for p in self.players:
            if p.name == name:
                return p
            
        return None
    
    def GetPlayerById(self, id: int) -> player.Player | None:
        for p in self.players:
            if p.id == id:
                return p
            
        return None
    
    def HandleIncommingPacket(self, connId: int, connectionManager, netPacket: NetPacket) -> bool:
        pass

    
class LobbyManager(object):
    lobbies: dict[int, Lobby] = {}
    
    def __init__(self) -> None:
        pass
    
    def AddLobby(self, lobbyId: int) -> bool:
        if self.lobbies.get(lobbyId) != None:
            return False
        
        self.lobbies[lobbyId] = Lobby()

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
    
    def GetLobbyAndPlayerForConnId(self, connId: int) -> tuple[Lobby, player.Player] | None:
        for lobbyId in self.lobbies:
            lobby: Lobby = self.lobbies[lobbyId]
            
            for p in lobby.players:
                if p.connectionId == connId:
                    return (lobby, p)
                
        return None
    
    def GetPlayerByName(self, playerName: str) -> player.Player | None:
        for lobbyId in self.lobbies:
            lobby: Lobby = self.lobbies[lobbyId]
            
            p: player.Player = lobby.GetPlayerByName(playerName)
            
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
                cm.SendPacket(connId, JoinNetPacket(incomming=True, playerId=JoinNetPacket.InvalidPlayerId()))
                return False
            
            playerId: int = JoinNetPacket.InvalidPlayerId()
            lobby: Lobby = self.GetLobby(joinPacket.lobbyId)
            
            # Add the player to the lobby if it exists
            if lobby != None:
                playerId = lobby.AddPlayer(player.Player(joinPacket.playerName, connId))
                
                DebugLog(f"Player ID result: {playerId}")
                
                if playerId < 0:
                    playerId = JoinNetPacket.InvalidPlayerId()
            
            # Send the response packet to the client
            cm.SendPacket(connId, JoinNetPacket(incomming=True, playerId=playerId))
        elif packetType == NetPacketType.LEAVE_LOBBY:            
            result: tuple[Lobby, player.Player] = self.GetLobbyAndPlayerForConnId(connId)
            
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
            cm.SendPacket(connId, CreateLobbyPacket(clientbound=True, lobbyId=lobbyId))   
        
        return True