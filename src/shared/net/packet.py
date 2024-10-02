import enum

class NetPacketType(enum.Enum):
    INVAL = -1
    # (Outgoing) Creates a lobby for other clients to join
    # Parameters:
    #   0: lobby id (2 bytes)
    #   1: max player count (1 byte)
    CREATE_LOBBY = 0
    # (Outgoing) Destroys the current lobby, if the sender is also the creator of the lobby
    # No parameters
    DESTROY_LOBBY = 1
    # (Outgoing) Starts the current lobby, if the sender is also the creator of the lobby
    # No parameters
    START_LOBBY = 2
    # (Outgoing) Restarts the current lobby, if the sender is also the creator of the lobby and
    # if the game has ended
    # No parameters
    RESTART_LOBBY = 3
    
    # (Outgoing/Incomming) Client X sends this to the server to join a lobby, server resends
    # this packet back as a confirmation, with the players player ID.
    # Packet flags: NETPACKET_FLAG_EXPECT_RESP
    # (Outgoing) Parameters:
    #   0: Lobby ID (2 bytes)
    #   1: Player name (X bytes)
    # 
    # (Incomming) Parameters:
    #   0: Player ID (1 byte)
    JOIN_LOBBY = 4
    # (Incomming) Notifies the client that a certain player has joined the lobby
    # Parameters:
    #   0: Player ID (1 byte)
    #   1: Player name (X bytes)
    NOTIFY_JOIN_LOBBY = 5
    # (Outgoing) Client X sends this to the server to leave a lobby
    # Parameters:
    #   0: Lobby ID (2 bytes)
    LEAVE_LOBBY = 6
    # (Incomming) Notifies the client that a certain player has left the lobby
    # Parameters:
    #   0: Player ID (1 byte)
    NOTIFY_LEAVE_LOBBY = 7
    
    # (Outgoing/Incomming) Client X sends this in order to signal it wants
    # to play a card, server sends a response packet to confirm that the play was legal
    # or not. If it wasn't legal, the server expects the client to send a new PLAY_CARD
    # packet. Otherwise it will notify the other players with sending them NOTIFY_PLAY_CARD packets
    # Packet flags: NETPACKET_FLAG_EXPECT_RESP
    # (Outgoing) Parameters:
    #   0: Card index (1 byte)
    #
    # (Incomming) Parameters:
    #   0: Play status (1 byte) : 1 = OK, 0 = Invalid play
    #   1: Next player ID (1 byte)
    PLAY_CARD = 8
    # (Incomming) Server sends this to all clients to notify them that a player has played
    # a card.
    # (Incomming) Parameters:
    #   0: Card (1 byte)
    #    - bits 0-4: card value from 2 to 15, where 11 to 14 are J,Q,H,A and 15 is a joker
    #    - bits 5-8: card type (Spades, Clubs, Diamonds, Hearts)
    #   1: Player ID (1 byte)
    #   2: Next player ID (1 byte) : Indicates which player is currently in turn
    NOTIFY_PLAY_CARD = 9
    
    # (Outgoing) Sent by the client if it had to reject a packet from the server.
    # Server should simply resend in most cases
    PACKET_REJECTED = 255
    
    def __int__(self) -> int:
        return self.value
    
# The current version of the server    
DEFAULT_VERSION: int = 1

# NetPacket flags
# Is this packet incomming (as seen from the client)
NETPACKET_FLAG_INCOMMING: int =     0x01
# Does this NetPacket expect a response (No response will be seens as a network error)
NETPACKET_FLAG_EXPECT_RESP: int =   0x02

class NetPacket(object):
    type: NetPacketType = NetPacketType.INVAL
    flags: int = 0
    version: int = 0
    rawData: bytes = []
    
    # Creates a netpacket object based on incomming data
    def __init__(self, type=NetPacketType.INVAL, flags=0, version=0, data: bytes=None) -> None:
        
        self.type = type
        self.flags = flags
        self.version = version
        # Store the raw data inside the packet
        self.rawData = data

        self.unmarshal(data)
                    
    def hasFlags(self, flags: int) -> bool:
        return (self.flags & flags) == flags
            
    def fromPacket(self, netPacket):
        if not netPacket:
            return
        
        self.unmarshal(netPacket.rawData)
        
        return self
    
    def unmarshal(self, data: bytes):
        if data == None or len(data) < 4:
            return
        
         # Try to parse the things xD
        try:
            # Parse the default data from the first 4 bytes
            self.type = NetPacketType(data[0])
            self.flags = int(data[1])
            self.version = int((data[2] << 8) | data[3])
        except ValueError:
            pass
    
    # Base function to marshal a network packet into a datastream
    def marshal(self) -> bytearray:
        ret: bytearray = bytearray()
        
        ret.append(int(self.type) & 0xff)
        ret.append(self.flags & 0xff)
        ret.append((self.version >> 8) & 0xff)
        ret.append(self.version & 0xff)
        
        return ret