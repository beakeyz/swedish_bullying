import enum

class NetPacketType(enum.Enum):
    INVAL = -1
    # (Serverbound) Creates a lobby for other clients to join
    # Parameters:
    #   0: lobby id (2 bytes)
    #   1: max player count (1 byte)
    CREATE_LOBBY = 0
    # (Serverbound) Destroys the current lobby, if the sender is also the creator of the lobby
    # No parameters
    DESTROY_LOBBY = 1
    # (Serverbound) Starts the current lobby, if the sender is also the creator of the lobby
    # Parameters: No parameters
    START_LOBBY = 2
    # (Serverbound) Restarts the current lobby, if the sender is also the creator of the lobby and
    # if the game has ended
    # No parameters
    RESTART_LOBBY = 3
    
    # (Serverbound/Clientbound) Client X sends this to the server to join a lobby, server resends
    # this packet back as a confirmation, with the players player ID.
    # Packet flags: NETPACKET_FLAG_EXPECT_RESP
    # (Serverbound) Parameters:
    #   0: Lobby ID (2 bytes)
    #   1: Player name (X bytes)
    # 
    # (Clientbound) Parameters:
    #   0: Player ID (1 byte)
    #   1: Lobby ID (2 bytes)
    #   2: Playercount already in the lobby (1 byte)
    #   3 -> X: Players already in the lobby (? bytes)
    #    - 0: Name string terminated by a null byte
    #    - 1: Player ID (1 byte)
    JOIN_LOBBY = 4
    # (Clientbound) Notifies the client that a certain player has joined the lobby
    # Parameters:
    #   0: Player ID (1 byte)
    #   1: Player name (X bytes)
    NOTIFY_JOIN_LOBBY = 5
    # (Serverbound) Client X sends this to the server to leave its lobby
    # Parameters: No parameters
    LEAVE_LOBBY = 6
    # (Clientbound) Notifies the client that a certain player has left the lobby
    # Parameters:
    #   0: Player ID (1 byte)
    NOTIFY_LEAVE_LOBBY = 7
    
    # (Serverbound/Clientbound) Client X sends this in order to signal it wants
    # to play a card, server sends a response packet to confirm that the play was legal
    # or not. If it wasn't legal, the server expects the client to send a new PLAY_CARD
    # packet. Otherwise it will notify the other players with sending them NOTIFY_PLAY_CARD packets
    # Packet flags: NETPACKET_FLAG_EXPECT_RESP
    # (Serverbound) Parameters:
    #   0: Card index (1 byte)
    #
    # (Clientbound) Parameters:
    #   0: Play status (1 byte) : 1 = OK, 0 = Invalid play
    #   1: Next player ID (1 byte)
    PLAY_CARD = 8
    # (Clientbound) Server sends this to all clients to notify them that a player has played
    # a card.
    # (Clientbound) Parameters:
    #   0: Card (2 byte)
    #    - byte 0: card value from 2 to 15, where 11 to 14 are J,Q,H,A and 15 is a joker
    #    - byte 1: card type (Spades, Clubs, Diamonds, Hearts)
    #   1: Player ID (1 byte)
    #   2: Next player ID (1 byte) : Indicates which player is currently in turn
    NOTIFY_PLAY_CARD = 9
    # (Serverbound/Clientbound) Client sends this when it wants to know what lobbies there are
    # Packet flags: NETPACKET_FLAG_EXPECT_RESP
    # (Serverbound) Parameters:
    #   0: lobbycount (2 bytes)
    #
    # (Clientbound) Parameters:
    #   0: Lobbycount (2 bytes)
    #   1 -> Lobbycount-1: Lobby IDs (2 * lobbycount bytes)
    LIST_LOBBIES = 10

    SELECT_OPEN_CARDS = 11
    # (Clientbound) Sent by the server to indicate that a client needs to take cards into their hand
    # The cards in the hand of the players are sorted based on value and type value both on the client
    # and on the server side, such that card indices are synced on both sides
    # Parameters:
    #   0: Next player ID (1 byte)
    #   1 -> X: Card X (2 bytes)
    TAKE_CARDS = 12
    # (Clientbound) Notifies clients that the game has started
    # Parameters:
    #   0-5: Hand card 0-5 (2*6=12 bytes)
    NOTIFY_START_GAME = 13
    NOTIFY_END_GAME = 14
    
    NOTIFY_TAKE_CARDS = 15
    
    OK_PING = 254
    # (Serverbound) Sent by the client if it had to reject a packet from the server.
    # Server should simply resend in most cases
    PACKET_REJECTED = 255
    
    
    def __int__(self) -> int:
        return self.value
    
# The current version of the server    
DEFAULT_VERSION: int = 1

# NetPacket flags
# Is this packet Clientbound (as seen from the client)
NETPACKET_FLAG_CLIENTBOUND: int =     0x01
# Does this NetPacket expect a response (No response will be seens as a network error)
NETPACKET_FLAG_EXPECT_RESP: int =   0x02

class NetPacketStream(bytes):
    idx: int = 0
        
    def __init__(self, bytes=None) -> None:
        self.idx = 0
        
    def reset(self) -> None:
        self.idx = 0
    
    def consume(self) -> (int | None):
        ret: int
        
        # print(f"NetPackeStream: consume ({self.idx}/{len(self)})")
        
        # Check if we still have bytes left to consume
        if self.idx >= len(self):
            return None
        
        # Grab the byte
        ret = self[self.idx]
        
        # Add one
        self.idx += 1
        
        return ret

class NetPacket(object):
    type: NetPacketType = NetPacketType.INVAL
    flags: int = 0
    version: int = 0
    rawData: NetPacketStream = []
    
    # Creates a netpacket object based on Clientbound data
    def __init__(self, type=NetPacketType.INVAL, flags=0, version=0, data: bytes|None=None) -> None:
        
        self.type = type
        self.flags = flags
        self.version = version
        
        # Store the raw data inside the packet
        if data != None:
            data = NetPacketStream(data)
            self.rawData = data

            self.unmarshal(data)
                    
    def hasFlags(self, flags: int) -> bool:
        return (self.flags & flags) == flags
    
    # Is this packet heading to the client
    def isClientBound(self) -> bool:
        return self.hasFlags(NETPACKET_FLAG_CLIENTBOUND)
    
    # Is this packet heading to the server
    def isServerBound(self) -> bool:
        return not self.hasFlags(NETPACKET_FLAG_CLIENTBOUND)
    
    def isNotifyPacket(self) -> bool:
        '''
        Here we specify which cards we consider 'notification packets'
        
        Notification packets are packets that the server can send to any client at any
        time. The subsequent client should be polling for these notifications and handling
        them ASAP
        '''
        return (
            self.type == NetPacketType.NOTIFY_JOIN_LOBBY or
            self.type == NetPacketType.NOTIFY_LEAVE_LOBBY or
            self.type == NetPacketType.NOTIFY_PLAY_CARD or
            self.type == NetPacketType.NOTIFY_START_GAME or
            self.type == NetPacketType.NOTIFY_END_GAME or
            self.type == NetPacketType.NOTIFY_TAKE_CARDS or
            self.type == NetPacketType.TAKE_CARDS
        )
            
    def fromPacket(self, netPacket):
        if not netPacket:
            return
        
        self.unmarshal(netPacket.rawData)
        
        return self
    
    def unmarshal(self, data: NetPacketStream):
        '''
        Unpacks the data from a bytestream sent over TCP into the actual netpacket object
        '''
        if data == None or len(data) < 4:
            return
        
        data.reset()
        
         # Try to parse the things xD
        try:
            # Parse the default data from the first 4 bytes
            self.type = NetPacketType(data.consume())
            self.flags = int(data.consume())
            self.version = int((data.consume() << 8) | data.consume())
        except ValueError:
            pass
    
    # Base function to marshal a network packet into a datastream
    def marshal(self) -> bytearray:
        '''
        Packs the data from this packet into a bytestream that can be sent over the TCP connection
        '''
        ret: bytearray = bytearray()
        
        ret.append(int(self.type) & 0xff)
        ret.append(self.flags & 0xff)
        ret.append((self.version >> 8) & 0xff)
        ret.append(self.version & 0xff)
        
        return ret
    
    def HandleServerBound(self) -> int:
        '''
        Pretty much an abstract function, since a generic netpacket has no clue how to handle itself
        
        Every concrete packet type class needs to implement this for themselves
        '''
        return 0

    def HandleClientBound(self) -> int:
        '''
        Pretty much an abstract function, since a generic netpacket has no clue how to handle itself
        
        Every concrete packet type class needs to implement this for themselves
        '''
        return 0

    def Handle(self) -> int:
        '''
        Handles the packet based on the direction it's going
        '''
        if self.isClientBound():
            return self.HandleClientBound()
        
        return self.HandleServerBound()
