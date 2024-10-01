from twisted.internet.interfaces import IAddress
from twisted.internet.protocol import Factory
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor

import server.conn as conn

class ServerConnFactory(Factory):
    def __init__(self, server) -> None:
        self.server = server

    def buildProtocol(self, addr: IAddress) -> conn.Protocol | None:
        return conn.ServerConnection(self, self.server)
    
class InternalServerConnection(object):
    __connection: conn.ServerConnection

    def __init__(self, connection) -> None:
        self.__connection = connection

class Server(object):

    connections: list[InternalServerConnection]

    def __init__(self, port) -> None:
        # Create an empty list
        self.connections = []

        # Initialize the TCP endpoint
        self.endpoint = TCP4ServerEndpoint(reactor, port)

        # Let the default server connection factory listen on this endpoint
        self.endpoint.listen(ServerConnFactory(self))

        # Run this bitch
        reactor.run()
        pass

    def __generateConnectionId(self, connection: conn.ServerConnection) -> int:
        pass

    # Should be called when a connection is created
    # by the connection factory
    def serverMakeConnection(self, connection: conn.ServerConnection) -> int:

        connection.connId = self.__generateConnectionId(self, connection)

        if connection.connId < 0:
            return connection.connId

        self.connections.append(InternalServerConnection(connection))

        return 0