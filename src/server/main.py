import srv as s
import connectManager
import debug.log as log

# Execution starts here
def main():
    print("Server started!")
    
    log.EnableDebug()

    cm = connectManager.ConnectionManager()
    s.Server(8007, cm)
    
    pass

if __name__ == "__main__":
    main()