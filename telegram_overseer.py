from src import printcolors as pc
import asyncio
from src.credential_handler import OverseerCredentialManager
from src.telegram_scraper import TelegramScraper
from src.data_analysis import CleanAndSave
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style


# A function to display the welcome banner at the start of the program
def welcome() -> None:
    pc.printout("-" * 80 + "\n")
    pc.printout(" @@@@@@   @@@  @@@  @@@@@@@@  @@@@@@@    @@@@@@   @@@@@@@@  @@@@@@@@  @@@@@@@ \n", pc.GREEN)
    pc.printout("@@@@@@@@  @@@  @@@  @@@@@@@@  @@@@@@@@  @@@@@@@   @@@@@@@@  @@@@@@@@  @@@@@@@@\n", pc.GREEN)
    pc.printout("@@!  @@@  @@!  @@@  @@!       @@!  @@@  !@@       @@!       @@!       @@!  @@@\n", pc.GREEN)
    pc.printout("!@!  @!@  !@!  @!@  !@!       !@!  @!@  !@!       !@!       !@!       !@!  @!@\n", pc.GREEN)
    pc.printout("@!@  !@!  @!@  !@!  @!!!:!    @!@!!@!   !!@@!!    @!!!:!    @!!!:!    @!@!!@! \n", pc.GREEN)
    pc.printout("!@!  !!!  !@!  !!!  !!!!!:    !!@!@!     !!@!!!   !!!!!:    !!!!!:    !!@!@!  \n", pc.GREEN)
    pc.printout("!!:  !!!  :!:  !!:  !!:       !!: :!!        !:!  !!:       !!:       !!: :!! \n", pc.GREEN)
    pc.printout(":!:  !:!   ::!!:!   :!:       :!:  !:!      !:!   :!:       :!:       :!:  !:!\n", pc.GREEN)
    pc.printout("::::: ::    ::::     :: ::::  ::   :::  :::: ::    :: ::::   :: ::::  ::   :::\n", pc.GREEN)
    pc.printout(" : :  :      :      : :: ::    :   : :  :: : :    : :: ::   : :: ::    :   : :\n", pc.GREEN)
    print("\n")
    pc.printout("Code structure based on OSINTagram\n", pc.YELLOW)
    pc.printout("1.01 - Developed by Alberto Federico Olivieri\n\n", pc.CYAN)
    pc.printout("Type 'list' to show all allowed commands\n")
    pc.printout("-" * 80 + "\n")

# A function to display the command list
def cmdlist() -> None:
    pc.printout("credentials\t\t")
    pc.printout("Provide all credentials saved, or set them if they are missing\n", colour=pc.YELLOW)
    pc.printout("set_api_id\t\t")
    pc.printout("Change saved API ID\n", colour=pc.YELLOW)
    pc.printout("set_api_hash\t\t")
    pc.printout("Change saved API HASH\n", colour=pc.YELLOW)
    pc.printout("set_phone_number\t")
    pc.printout("Change saved PHONE NUMBER, remember international prefix\n", colour=pc.YELLOW)
    pc.printout("set_username\t\t")
    pc.printout("Change saved USERNAME\n", colour=pc.YELLOW)
    pc.printout("targets\t\t\t")
    pc.printout("Provide all targets saved\n", colour=pc.YELLOW)
    pc.printout("set_targets\t\t")
    pc.printout("Set target group(s)\n", colour=pc.YELLOW)
    pc.printout("reset_targets\t\t")
    pc.printout("Clear all target group(s)\n", colour=pc.YELLOW)
    pc.printout("save_targets\t\t")
    pc.printout("Save all target(s)\n", colour=pc.YELLOW)
    pc.printout("load_targets\t\t")
    pc.printout("Load all saved target(s)\n", colour=pc.YELLOW)
    pc.printout("date\t\t\t")
    pc.printout("Provide date saved\n", colour=pc.YELLOW)
    pc.printout("set_start_date\t\t")
    pc.printout("Set date from which data will be collected, if no date set, it will be retrieved from the beginning\n", colour=pc.YELLOW)
    pc.printout("set_end_date\t\t")
    pc.printout("Set date from which data will stopped to be collected, if no date set, it will be retrieved until yesterday\n", colour=pc.YELLOW)
    pc.printout("reset_date\t\t")
    pc.printout("Clear all dates\n", colour=pc.YELLOW)
    pc.printout("retrieve_messages\t")
    pc.printout("Retrieve messages from target group(s) and save the result in a JSON and in the SQLite DB\n", colour=pc.YELLOW)
    pc.printout("delete_double_data\t")
    pc.printout("Delete doubled data in the SQLite database\n", colour=pc.YELLOW)
    pc.printout("full_replies_view\t")
    pc.printout("Create a view called full_replies in SQLite with all the messages and their replies, it could take a while, use carefully\n", colour=pc.YELLOW)
    pc.printout("engagement\t\t")
    pc.printout("Extracts top engagement statistics and saves them in csv\n", colour=pc.YELLOW)
    pc.printout("reaction_data\t\t")
    pc.printout("Creates a csv with a sum of all reaction per reaction type. It also output the top post per top reaction\n", colour=pc.YELLOW)
    pc.printout("wordclouds\t\t")
    pc.printout("Create two wordclouds, one from the target posts, one from target posts and replies\n", colour=pc.YELLOW)
    pc.printout("add_stopwords\t\t")
    pc.printout("Add custom stopwords for the wordcloud\n", colour=pc.YELLOW)
    pc.printout("show_stopwords\t\t")
    pc.printout("Show custom stopwords for the wordcloud\n", colour=pc.YELLOW)
    pc.printout("remove_stopwords\t")
    pc.printout("Remove custom stopwords for the wordcloud\n", colour=pc.YELLOW)
    pc.printout("frequency\t\t")
    pc.printout("Exctract the 24h and weekly frequency of posts of the targets\n", colour=pc.YELLOW)
    pc.printout("keywords_search\t\t")
    pc.printout("Save the posts containing the keyword in an excel spreadsheet, needs a start date\n", colour=pc.YELLOW)


# A completer function for command completion
def completer(text: str, state: int) -> str or None:
    options = [i for i in commands if i.startswith(text)]
    if state < len(options):
        return options[state]
    else:
        return None

# A function to exit program
def _quit() -> None:
    pc.printout("Goodbye!\n", pc.RED)
    exit(0)

# Instantiate required classes
OverseerCred = OverseerCredentialManager()
TScap = TelegramScraper()
CeS = CleanAndSave()
# Commands dictionary to map command names to their respective function
commands = {
    'list': cmdlist,
    'help': cmdlist,
    'quit': _quit,
    'exit': _quit,
    'credentials': OverseerCred.print_credentials,
    'set_api_id': OverseerCred.set_api_id,
    'set_api_hash': OverseerCred.set_api_hash,
    'set_phone_number': OverseerCred.set_phone,
    'set_username': OverseerCred.set_username,
    'targets': TScap.retrieve_targets,
    'set_targets': TScap.add_targets,
    'reset_targets': TScap.reset_targets,
    'save_targets': TScap.save_targets,
    'load_targets': TScap.load_targets,
    'retrieve_messages': TScap.main_loop_clean_and_save,
    'date': TScap.retrieve_date,
    'set_start_date': TScap.add_date,
    'set_end_date': TScap.add_end_date,
    'reset_date': TScap.reset_date,
    'delete_double_data': CeS.clean_sql_tables,
    'full_replies_view': CeS.create_full_replies_view,
    'engagement': CeS.engagement,
    'reaction_data': CeS.reaction_data,
    'wordclouds': CeS.wordclouds,
    'add_stopwords': CeS.add_stopwords,
    'show_stopwords': CeS.show_custom_stopwords,
    'remove_stopwords': CeS.remove_custom_stopwords,
    'frequency': CeS.frequency,
    'keywords_search': CeS.search_keywords
}

command_completer = WordCompleter(['list', 'help', 'quit', 'exit', 'credentials', 'set_api_id', 'set_api_hash',
                                   'set_phone_number', 'set_username', 'targets', 'set_targets', 'reset_targets',
                                   'save_targets', 'load_targets', 'date', 'set_start_date', 'set_end_date',
                                   'reset_date', 'retrieve_messages', 'delete_double_data', 'full_replies_view',
                                   'engagement', 'reaction_data', 'wordclouds', 'add_stopwords', 'show_stopwords',
                                   'remove_stopwords', 'frequency', 'keywords_search'], ignore_case=True)

# Define your CLI style (optional)
style = Style.from_dict({'': '#ffffff', 'completion-menu.completion': 'bg:#008888 #ffffff',
                         'completion-menu.completion.current': 'bg:#00aaaa #000000',
                         'scrollbar.background': 'bg:#88aaaa', 'scrollbar.button': 'bg:#222222',})

# Initialize PromptSession
session = PromptSession(completer=command_completer, style=style)

# Command execution function
def execute_command(cmd):
    _cmd = commands.get(cmd)
    if _cmd:
        if asyncio.iscoroutinefunction(_cmd):
            asyncio.run(_cmd())
        else:
            _cmd()
    elif cmd == "":
        print("")
    else:
        pc.printout("Unknown command\n", pc.RED)

# Main program loop using prompt_toolkit
def main():
    welcome()
    while True:
        try:
            # Get user input using prompt_toolkit
            cmd = session.prompt("Run a command: ", style=style)
            execute_command(cmd)
        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            pc.printout("\nGoodbye!\n", pc.RED)
            break
        except EOFError:
            # Handle Ctrl+D gracefully
            pc.printout("\nGoodbye!\n", pc.RED)
            break

if __name__ == "__main__":
    main()
