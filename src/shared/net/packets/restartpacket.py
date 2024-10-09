from ..packet import *

# Doesn't carry any extra data, simply tells the lobby to restart the game
class RestartPacket(NetPacket):
    def __init__(self) -> None:
        super().__init__(NetPacketType.RESTART_LOBBY, 0, 1, None)