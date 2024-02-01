import json
import os
import pickle
import telethon.errors.rpcerrorlist
from pytz import timezone
from src.credential_handler import OverseerCredentialManager
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.errors import ChatAdminRequiredError
from datetime import datetime, timedelta
from tzlocal import get_localzone_name
from src.data_analysis import CleanAndSave
import src.printcolors as pc


class DateTimeEncoder(json.JSONEncoder):
    """
    A class to handle date-time encoding.
    """
    def default(self, o) -> str | list | json.JSONEncoder:
        """
        Default method for date-time encoding.

        Takes as input an object and returns the ISO-formatted
        string if the object is datetime, a list if the object is bytes,
        or uses the default JSONEncoder method to convert the object to JSON.

        Params:
        ------
        o : object
            The object that needs to be converted to JSON.

        Returns:
        -------
        str | list | json.JSONEncoder
            The ISO-formatted datetime string if o is of datetime type,
            list if o is bytes object
            or JSON representation of the object
        """
        if isinstance(o, datetime):
            # If the object is a datetime object,
            # convert it to an ISO-formatted string
            return o.isoformat()

        if isinstance(o, bytes):
            # If the object is a bytes object, convert it to a list
            return list(o)

        # If the object is of other type, use default JSON Encoder's default method
        return json.JSONEncoder.default(self, o)


class TelegramScraper:
    """
    A class used to scrape and handle information from Telegram.
    """
    TZ = get_localzone_name() # Get the local timezone name
    # Retrieve credentials from the OverseerCredentialManager to use for the Telegram Scraper
    api_id, api_hash, phone, username = OverseerCredentialManager().retrieve_creds()

    def __init__(self) -> None:
        """
        Constructs all the necessary attributes for the telegram scraper object.
        Initializes the Telegram Client with provided username, api_id and api_hash.
        """
        self.end_date = None
        self.targets = [] # Initialize targets as empty list
        self.offset_date = None
        # Setting midnight timing constraint
        self.not_after_today_midnight = timezone(self.TZ).localize(
            datetime.replace(datetime.today(), hour=00, minute=00, second=00, microsecond=0000))
        # Initialize the Telegram Client
        self.client = TelegramClient(self.username, api_id=self.api_id, api_hash=self.api_hash)

    def add_targets(self) -> None:
        """
        Adds new message targets to the target list.
        Messages will be retrieved from these targets.

        Contains functions to read user's input and add them to the targets list

        Returns
        -------
        None
        """
        # Remind user to reset targets if they are already set
        if self.targets:
            pc.printout("Targets are already set, if you continue you will add more targets.\n", pc.RED)
            pc.printout("If you wanna reset targets use reset_targets\n", pc.RED)
        # Instruct user to input telegram URLs
        # Then implement user input to add targets
        pc.printout("Please, enter one or more Telegram URLs (ex: https://t.me/XXXXX)\n", pc.CYAN)
        pc.printout("Separate the URLs with a comma\n", pc.CYAN)
        targets = input()
        # Loop through and add targets removing white spaces
        for target in targets.split(','):
            target = target.lstrip().rstrip()
            self.targets.append(target)

    def retrieve_targets(self) -> None:
        """
        Prints all message targets in the target list or an
        error message if no targets are set.

        Returns
        -------
        None
        """
        # Check if any targets are set
        if not self.targets:
            pc.printout("No target(s) Group(s) is set\n", pc.RED)
        else:
            # Loop through and print all the targets
            for target in self.targets:
                pc.printout("{}\n".format(target), pc.RED)

    def reset_targets(self) -> None:
        """
        Resets all message targets in the target list empty.

        Returns
        -------
        None
        """
        self.targets = []

    def save_targets(self) -> None:
        """
        Saves the message targets to a pickle file for persistence.

        Returns
        -------
        None
        """
        # Check if targets exist before trying to save
        if self.targets:
            with open("./credentials/targets.pkl", "wb") as file:
                pickle.dump(self.targets, file)
                file.close()
        else:
            pc.printout("No target(s) to save\n", pc.RED)

    def load_targets(self) -> None:
        """
        Load the message targets from a pickle file if it exists.

        Returns
        -------
        None
        """
        if os.path.exists('./credentials/targets.pkl'):
            with open("./credentials/targets.pkl", "rb") as file:
                self.targets = pickle.load(file)
                file.close()
        else:
            pc.printout("No target(s) is saved\n", pc.RED)

    def add_date(self) -> None:
        """
        Adds a new date for retrieving messages.

        Returns
        -------
        None
        """
        pc.printout("Please, enter a date (dd/mm/YYYY), if no date is set, all messages will be retrieved\n", pc.CYAN)
        pc.printout("With a date, messages will be retrieved from that date to yesterday\n", pc.CYAN)
        date_input = input()
        date_input = timezone(self.TZ).localize(datetime.strptime(date_input, "%d/%m/%Y"))
        self.offset_date = date_input

    def add_end_date(self) -> None:
        """
        Adds an end date for retrieving messages until.

        Returns
        -------
        None
        """
        pc.printout("Please, enter a date (dd/mm/YYYY), if no date is set data will be retrieved until yesterday\n", pc.CYAN)
        pc.printout("With a date, messages will be retrieved from start date to this date (excluded)\n", pc.CYAN)
        date_input = input()
        date_input = timezone(self.TZ).localize(datetime.strptime(date_input, "%d/%m/%Y"))
        self.end_date = date_input

    def retrieve_date(self) -> None:
        """
        Retrieves the date set for message retrieval. If no date is set, it informs the user.

        Returns
        -------
        None
        """
        # Check if any date is set
        if not self.offset_date:
            pc.printout("No date is set\n", pc.RED)
        else:
            # Print the start and end dates
            pc.printout("Start date:{}\n".format(datetime.strftime(self.offset_date, "%d/%m/%Y")), pc.RED)
            if not self.end_date:
                pc.printout("Start date:{}\n".format(datetime.strftime(self.not_after_today_midnight, "%d/%m/%Y")), pc.RED)
            else:
                pc.printout("Start date:{}\n".format(datetime.strftime(self.end_date, "%d/%m/%Y")), pc.RED)

    def reset_date(self) -> None:
        """
        Resets the date set for message retrieval to None.

        Returns
        -------
        None
        """
        self.offset_date = None
        self.end_date = None

    async def auth_check(self) -> None:
        """
        Checks and handles the authorization of the user in an asynchronous manner.
        Starts the client and checks the user's authorization.
        If the user is not authorized, the code is sent to the phone number associated with the user.
        Prompts the user to enter the received code. If a SessionPasswordNeededError error is raised, the user is prompted to enter the password else.

        Raises
        ------
        SessionPasswordNeededError
            If a password is required to sign in.

        Returns
        -------
        None
        """
        # Start the client
        await self.client.start()
        pc.printout("Client auth check initiated\n")
        # Check if user is authorized
        # If not, initiate authorization process and handle potential SessionPasswordNeededError
        if not await self.client.is_user_authorized():
            await self.client.send_code_request(self.phone)
            try:
                pc.printout('Please, enter the code you received: \n', pc.CYAN)
                await self.client.sign_in(self.phone, input())
            except SessionPasswordNeededError:
                pc.printout('Please, enter your password: \n', pc.CYAN)
                await self.client.sign_in(password=input())

    async def retrieve_messages(self, target, include_replies=True) -> None:
        """
        Asynchronously retrieves messages from a specified Telegram channel.
        Optionally retrieves replies to each message if include_replies is True.

        Parameters:
        target (str): The Telegram channel URL or identifier.
        include_replies (bool): Flag to determine whether to retrieve replies.

        Returns:
        None: Saves messages and, optionally, their replies in JSON files.
        """
        # Start the client
        await self.client.get_me()
        channel_name = target.split("/")[-1]
        entity = channel_name
        print(target)
        target_channel = await self.client.get_entity(entity)
        all_messages = []
        # Check if end date set else set to yesterday
        if not self.end_date:
            not_after_selected_date = self.not_after_today_midnight
            last_date = datetime.strftime(datetime.now() - timedelta(1), '%d_%m_%Y')
        else:
            not_after_selected_date = self.end_date
            last_date = datetime.strftime(self.end_date, "%d_%m_%Y")
        # Prepare date for input
        if self.offset_date:
            date_input = datetime.strftime(self.offset_date, "%d_%m_%Y")
        else:
            date_input = 'beginning'
        # Prepare any directories required for saving messages
        try:
            os.makedirs('./output/channel_name_{}/from_{}_to_{}/replies_{}'
                        .format(channel_name, date_input, last_date, target_channel.id))
        except FileExistsError:
            pass
        errors = "This messages do not have their replies retrieved:"
        pc.printout("Starting message retrieval from {}\n".format(channel_name), pc.RED)
        # Asynchronously iterate through messages and retrieve replies
        async for message in self.client.iter_messages(target_channel,
                                                       reverse=True,
                                                       offset_date=self.offset_date):
            all_replies = []
            if message.date < not_after_selected_date:
                pc.printout("Retrieving message id number: {}\r".format(message.id))
                if include_replies:
                    try:
                        # Gather replies for each message
                        async for reply in self.client.iter_messages(target_channel,
                                                                     reverse=True,
                                                                     reply_to=message.id):
                            all_replies.append(reply.to_dict())
                        with open('./output/channel_name_{}/from_{}_to_{}/replies_{}/replies_data_{}.json'
                             .format(channel_name, date_input, last_date, target_channel.id, message.id), 'w') as outfile:
                            json.dump(all_replies, outfile, cls=DateTimeEncoder)
                    except telethon.errors.rpcerrorlist.MsgIdInvalidError:
                        errors += " {}".format(str(message.id))
                else:
                    pass
                all_messages.append(message.to_dict())
            else:
                pass
        with open('./output/channel_name_{}/from_{}_to_{}/messages_data_{}.json'
             .format(channel_name, date_input, last_date, target_channel.id), 'w') as outfile:
            json.dump(all_messages, outfile, cls=DateTimeEncoder)
        with open('./output/channel_name_{}/from_{}_to_{}/errors.txt'
             .format(channel_name, date_input, last_date), 'w') as handle:
            handle.write(errors)
        pc.printout("Messages retrieval from {} is finished\n".format(channel_name), pc.RED)

    async def retrieving_and_cleaning_messages(self) -> None:
        """
        Handles the full process of message retrieval and data cleaning.
        Iterates over each target, retrieves messages and replies, and cleans the data.

        Returns:
        None: The function orchestrates the retrieval and cleaning processes but does not return a value.
        """
        if not self.targets:
            pc.printout("No target(s) Group(s) is set\n", pc.RED)
        else:
            try:
                await self.auth_check()
                for target in self.targets:
                    pc.printout(f"Do you want to download replies for {target}? (yes/no): ", pc.CYAN)
                    user_input = input().lower()
                    include_replies = user_input == 'yes'
                    # start retrieving messages for all targets
                    await self.retrieve_messages(target=target, include_replies=include_replies)
                await self.client.disconnect()
                pc.printout("Saving messages in SQLite table...\n", pc.RED)
                clean_and_save = CleanAndSave()
                await clean_and_save.cleaning_process()
                pc.printout("Done!\n", pc.RED)
            except ChatAdminRequiredError:
                pc.printout("Chat admin privileges are required to do that in the specified chat\n", pc.RED)

    def main_loop_clean_and_save(self) -> None:
        """
        The main loop that initiates the message retrieval and data cleaning process.
        This function is the starting point when the script is executed.

        Returns:
        None: Drives the overall process but does not return a value.
        """
        self.client.loop.run_until_complete(self.retrieving_and_cleaning_messages())