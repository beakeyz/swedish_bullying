
class Player(object):
    name: str
    id: int
    connectionId: int
    
    def __init__(self, name, connectionId) -> None:
        self.name = name
        self.id = -1
        self.connectionId = connectionId
        
    def SetPlayerId(self, id: int) -> bool:
        if id >=  0:
            return False
        
        self.id = id

        return True
    
    def ResetPlayerId(self):
        self.id = -1