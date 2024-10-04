from ..packet import NetPacket, NetPacketType, NETPACKET_FLAG_CLIENTBOUND, NETPACKET_FLAG_EXPECT_RESP
from ...game.player import *

class JoinNetPacket(NetPacket):
    lobbyId: int | None
    playerId: int | None
    playerName: str | None
    nrGamePlayer: int | None
    gamePlayers: list[GamePlayer] | None = []

    def __init__(self, incomming=False, lobbyId=None, playerId=None, playerName=None, gamePlayers=None, data=None) -> None:
        super().__init__(type=NetPacketType.JOIN_LOBBY, flags=(NETPACKET_FLAG_CLIENTBOUND if incomming else 0) | NETPACKET_FLAG_EXPECT_RESP, version=1, data=data)
        
        self.lobbyId = lobbyId
        self.playerId = playerId
        self.playerName = playerName
        self.gamePlayers = gamePlayers
        
        if gamePlayers != None:
            self.nrGamePlayer = len(gamePlayers)
        else:
            self.nrGamePlayer = 0
        
    def InvalidPlayerId() -> int:
        return 0xff
        
    def isValidPlayerId(self) -> bool:
        return self.playerId != None and self.playerId < 0xff
        
    def unmarshal(self, data: bytes | None):
        if data == None:
            return
        
        super().unmarshal(data)
        
        if self.hasFlags(NETPACKET_FLAG_CLIENTBOUND):
            if len(data) >= 6:
                self.playerId = data[4]
                self.lobbyId = (data[5] << 8) | data[6]

            if len(data) >= 8:
                self.nrGamePlayer = min(data[7], 5)
                self.gamePlayers = []
                
                # print(f"Trying to parse {self.nrGamePlayer} from JoinNetPacket...")
                
                index = 8
                bytesLeft = len(data) - 8
                
                for i in range(self.nrGamePlayer):
                    playerName: str = ""
                    while bytesLeft and data[index] != 0x00:
                        playerName += chr(data[index])
                        index += 1
                        bytesLeft -= 1
                    
                    # print(f"Adding player {playerName} with ID {data[index+1]} to the gameplayers list")
                    
                    # Add this gameplayer
                    self.gamePlayers.append(GamePlayer(playerName, None, data[index+1], self.lobbyId))
                    
                    index += 2
                    bytesLeft -= 2
                    pass
        else:
            if len(data) >= 6:
                self.lobbyId = (data[4] << 8) | data[5]
                
                self.playerName = ""
                
                for i in range(len(data) - 6):
                    self.playerName += chr(data[6 + i])

    
    def marshal(self) -> bytearray:
        # Let NetPacket do the default header
        ret: bytearray = super().marshal()

        if self.hasFlags(NETPACKET_FLAG_CLIENTBOUND):
            if self.playerId is None or self.lobbyId is None:
                return ret

            ret.append(self.playerId & 0xff)
            ret.append((self.lobbyId >> 8) & 0xff)
            ret.append((self.lobbyId) & 0xff)

            if self.gamePlayers != None:
                ret.append((len(self.gamePlayers) & 0xff))
                
                # TODO: Marshal the playerlist
                # assert False , "TODO marsalah player list in JoinNetPacket"
                for p in self.gamePlayers:
                    for c in p.name:
                        ret.append(ord(c))
                    ret.append(0x00)

                    ret.append(p.playerId)
        else:
            if self.lobbyId is None or self.playerName is None:
                return ret
            ret.append((self.lobbyId >> 8) & 0xff)
            ret.append((self.lobbyId) & 0xff)
            
            # Simply append the chars to the stream
            for c in self.playerName:
                ret.append(ord(c))
        
        return ret
    
# Sent to every connected client in a lobby when a new player joins
class NotifyJoinPacket(NetPacket):
    playerName: str | None
    playerId: int | None
    
    def __init__(self, playerName=None, playerId=None) -> None:
        super().__init__(NetPacketType.NOTIFY_JOIN_LOBBY, NETPACKET_FLAG_CLIENTBOUND, 1, None)
        
        self.playerName = playerName
        self.playerId = playerId
        
        
    def unmarshal(self, data: bytes | None):
        if data == None:
            return
        
        super().unmarshal(data)
        
        if len(data) < 5:
            return
        
        self.playerId = data[4]
                
        self.playerName = ""
        
        for i in range(len(data) - 5):
            self.playerName += chr(data[5 + i])
    
    def marshal(self) -> bytearray:
        # Let NetPacket do the default header
        ret: bytearray = super().marshal()

        if self.playerId is None:
            return ret

        ret.append(self.playerId & 0xff)

        if self.playerName is None:
            return ret
            
        # Simply append the chars to the stream
        for c in self.playerName:
            ret.append(ord(c))
        
        return ret
