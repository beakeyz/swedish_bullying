# Layout of the network format

This file will explain (also to myself) how the network protocol for this game is going to be laid out

## Base network packets

This game is not very high paced, so high packet rates are not (or should not) be needed. We also don't really care about security (we do a bit,
but it's not our main concern). The most important thing this network format needs to do is to provide a programmer-friendly way to code up a playable
game over the wire, with as little complications as possible.

Every packet will be in pure binary (for now?) and they will have a 32-byte header in the following format:

byte 0: Packet type. We really shouldn't have more than 255 packet types (I hope lol)
byte 1: Packet flags
byte 2 - 3: Packet type. This way we can easily check if the client and the server are (roughly) on the same page

The length of the packet is handled for us by python

The different packet types are laid out in shared/packet.py and (as the location suggests) these packet structs are shared between client and server
to have ez sync thing