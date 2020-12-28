from sys import platform

class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

bold      = lambda s : color.BOLD      + s + color.END
underline = lambda s : color.UNDERLINE + s + color.END
colorize  = lambda s, col : (col + s + color.END) if 'linux' in platform else s

from sys import platform
from os import system

if 'win' in platform:
    def clear(): system('cls')
else:
    def clear(): system('clear')
