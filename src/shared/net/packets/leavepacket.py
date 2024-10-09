from ..packet import *

class LeavePacket(NetPacket):
    def __init__(self) -> None:
        super().__init__(NetPacketType.LEAVE_LOBBY, 0, 1)