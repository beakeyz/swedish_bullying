from ...shared.net.packets import *
from ...shared.game.player import GamePlayer

class Player(object):
    name: str
    id: int
    connectionId: int
    gamePlayer: GamePlayer
    
    def __init__(self, name, connectionId) -> None:
        self.name = name
        self.id = JoinNetPacket.InvalidPlayerId()
        self.connectionId = connectionId
        
    def SetPlayerId(self, id: int) -> bool:
        if self.id != JoinNetPacket.InvalidPlayerId():
            return False
        
        self.id = id

        return True
    
    def ResetPlayerId(self):
        self.id = JoinNetPacket.InvalidPlayerId()