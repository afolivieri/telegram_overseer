import sys
from curses import setupterm, tigetnum
from colorama import init, Fore, Style

# Define color codes for terminal output
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

color_map = {BLACK: Fore.BLACK,
             RED: Fore.RED,
             GREEN: Fore.GREEN,
             YELLOW: Fore.YELLOW,
             BLUE: Fore.BLUE,
             MAGENTA: Fore.MAGENTA,
             CYAN: Fore.CYAN,
             WHITE: Fore.WHITE}

def printout(text: str, colour: int = WHITE) -> None:
    """
    Function to print colored text to the console using Colorama.
    """
    color = color_map.get(colour, Fore.WHITE)
    sys.stdout.write(color + text + Style.RESET_ALL)

