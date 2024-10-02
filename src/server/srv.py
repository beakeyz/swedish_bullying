from twisted.internet.interfaces import IAddress
from twisted.internet.protocol import Factory
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor
from twisted.internet.protocol import Protocol

import conn

class ServerConnFactory(Factory):
    def __init__(self, server) -> None:
        self.server = server

    def buildProtocol(self, addr: IAddress) -> Protocol | None:
        return conn.ServerConnection(self, self.server.cm)

class Server(object):
    def __init__(self, port, cm) -> None:
        # Create an empty list
        self.connections = []

        # Initialize the TCP endpoint
        self.endpoint = TCP4ServerEndpoint(reactor, port)

        # Let the default server connection factory listen on this endpoint
        self.endpoint.listen(ServerConnFactory(self))
        
        # Set the internal connection manager
        self.cm = cm

        # Run this bitch
        reactor.run()
        pass