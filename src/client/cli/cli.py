import re

from ..net.network import NetworkClient

from ...shared.net.packets.joinpacket import JoinNetPacket

def __cli_help(input: str, argv: list[str], nc): 
    print("Available commands:")
    for c in __cli_commands:
        print(f" - {c}: {__cli_commands[c][1]}")
        
def __cli_exit(input: str, argv: list[str], nc: NetworkClient):
    nc.disconnect()

def __cli_join(input: str, argv: list[str], nc: NetworkClient):
    netResponse: JoinNetPacket = None
    lobbyId: int
    
    if len(argv) != 3:
        print("Please supply all the required arguments! (lobbyID and player name)")
        return
    
    try:
        lobbyId = int(argv[1])
    except:
        print("Please supply a valid lobby ID")
        return

    # Ask server to join
    response = nc.SendPacketAndAwaitResponse(JoinNetPacket(incomming=False, lobbyId=lobbyId, playerName=argv[2]))
    
    # Check if no oof
    if response == None:
        print("Failed to join that lobby")
        return
    
    # Transform
    netResponse: JoinNetPacket = JoinNetPacket().fromPacket(response)
    
    if netResponse.playerId == None:
        print("Failed to join that lobby =(")
        return
    
    print(f"Success! Player {argv[2]} joined with ID {netResponse.playerId}")

def __cli_leave(input: str, argv: list[str], nc: NetworkClient):
    pass

def __cli_create(input: str, argv: list[str], nc: NetworkClient):
    pass

def __cli_destroy(input: str, argv: list[str], nc: NetworkClient):
    pass

def __cli_start(input: str, argv: list[str], nc: NetworkClient):
    pass

__cli_commands = {
    "help": [__cli_help, "Display this info"],
    "exit": [__cli_exit, "Exits the application"],
    "join": [__cli_join, "Joins a lobby. Usage: join <lobby id> <player name>"],
    "leave": [__cli_leave, "Leaves the current lobby"],
    "create": [__cli_create, "Creates a new lobby. Usage: create <lobby id>"],
    "destroy": [__cli_destroy, "Destroys the current lobby"],
    "start": [__cli_start, "Starts the current lobby if there are enough players"],
}

def CliStep(input: str, nc: NetworkClient) -> int:
    argv: list[str] = input.split()
    func = None
    try:
        func = __cli_commands[argv[0]]
        
        if func == None:
            return 1
    except:
        return 1
    
    func[0](input, argv, nc)
    
    
    return 0