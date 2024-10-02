from colorama import Fore

global __enableDebug
__enableDebug: bool = False

__OKColor = Fore.GREEN
__WarningColor = Fore.YELLOW
__ErrorColor = Fore.RED
__DebugColor = Fore.CYAN
__NormalColor = Fore.WHITE

def EnableDebug() -> None:
    global __enableDebug
    __enableDebug = True
    
def DisableDebug() -> None:
    global __enableDebug
    __enableDebug = False
    
def DebugLog(fmt: str) -> None:
    global __enableDebug
    if not __enableDebug:
        return
    
    print(__DebugColor + "[DEBUG]: " + __NormalColor + fmt)
    
def ErrorLog(fmt: str) -> None:
    print(__ErrorColor + "[ERROR]: " + __NormalColor + fmt)
    
def WarningLog(fmt: str) -> None:
    print(__WarningColor + "[WARNING]: " + __NormalColor + fmt)
    
def OkLog(fmt: str) -> None:
    print(__OKColor + "[ OK ]: " + __NormalColor + fmt)