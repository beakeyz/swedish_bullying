from . import player

from ..debug.log import DebugLog
from ..connectManager import ConnectionManager

from ...shared.net.packet import NetPacket, NetPacketType
from ...shared.net.packets.joinpacket import JoinNetPacket


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
        self.players.append(pl)
        
        # Set the players ID
        pl.SetPlayerId(self.nextPlayerId)
        
        # Add one
        self.nextPlayerId += 1
    
        return pl.id
    
    def RemovePlayer(self, pl: player.Player) -> bool:
        if not self.nrPlayers:
            return False
        
        try:
            self.players.remove(pl)
        except:
            return False
        
        return True
    
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
    
    def GetLobby(self, lobbyId: int) -> Lobby:
        return self.lobbies.get(lobbyId)
    
    def HandleIncommingPacket(self, connId: int, cm: ConnectionManager, netPacket: NetPacket) -> bool:
        '''
        Parse the packet to figure out which lobby this packet is meant for
        '''
        packetType: NetPacketType = netPacket.type
        
        if packetType == NetPacketType.JOIN_LOBBY:
            joinPacket = JoinNetPacket().fromPacket(netPacket)
            
            DebugLog(f"Player {joinPacket.playerName} is trying to join lobby {joinPacket.lobbyId}")
            
            # TODO: Check if the player can join and let them join if they can
            
            # Create a response packet
            joinPacket = JoinNetPacket(incomming=True, lobbyId=joinPacket.lobbyId, playerId=69)
            
            # Send the response packet to the client
            cm.SendPacket(connId, joinPacket)
            
            
        
        pass