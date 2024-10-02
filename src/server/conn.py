from twisted.protocols.socks import SOCKSv4
from twisted.python.failure import Failure

from .connectManager import ConnectionManager
from .debug.log import DebugLog

# This server implements the twisted internet protocol
# 
# There will be an object of this class for every connection that is
# made to the server
#
# This component is responsible for passing the different twisted connection calls
# on to the connection manager. It will then in turn handle further connection states and stuff
class ServerConnection(SOCKSv4):
    connId: int
    cm: ConnectionManager

    def __init__(self, factory, cm) -> None:
        self.factory = factory
        self.connId = -1
        self.cm = cm
        super().__init__()

    def dataReceived(self, data: bytes) -> None:
        DebugLog("We've recieved some data!")
        DebugLog(f"Len={len(data)}, bytestream={data}")
        
        # Propegate the call to the connection manager
        self.cm.onDataRecieve(self.connId, data)
        
        # Write back the data as a test
        self.write(data)
        
        return super().dataReceived(data)
    
    def write(self, data):
        DebugLog(f"ServerConnection->write(self, data={data}) called!")
        
        # Propegate this call to the connection manager
        self.cm.onDataSend(self.connId, data)
        
        return super().write(data)
    
    def makeReply(self, reply, version=0, port=0, ip="0.0.0.0"):
        return super().makeReply(reply, version, port, ip)
    
    def connectionMade(self):
        DebugLog("Hey, someone connected to our server!")

        # Call the server to notify it of this connection
        self.connId = self.cm.registerConnection(super())

        return super().connectionMade()
    
    def connectionLost(self, reason: Failure = ...) -> None:
        DebugLog("Bye.. sad to see you go =(")
        
        # Remove this connection
        self.cm.unregisterConnection(self.connId)
        
        return super().connectionLost(reason)
    