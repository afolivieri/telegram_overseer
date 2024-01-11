import sys
from curses import setupterm, tigetnum

# Define color codes for terminal output
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

def has_colours(stream) ->bool:
    """
    Function to check if the output stream supports colours.
    It checks if the stream has 'isatty' attribute and it's True,
    then checks if the terminal supports more than 2 colours using curses module.
    """
    if not hasattr(stream, "isatty") or not stream.isatty():
        return False
    try:
        setupterm()
        return tigetnum("colors") > 2
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

# Check if the standard output (stdout) supports colours and save it as a global variable
supports_colours = has_colours(sys.stdout)

def printout(text: str, colour: int = WHITE) -> None:
    """
    Function to print coloured text to the console.
    If terminal supports colours, it formats the text with appropriate escape sequence,
    else it simply writes the text to the output.
    """
    if supports_colours:
        seq = "\x1b[1;%dm" % (30 + colour) + text + "\x1b[0m"
        sys.stdout.write(seq)
    else:
        sys.stdout.write(text)