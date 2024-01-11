import pickle
import os.path
from src import printcolors as pc


# This class manages the input, handling, and storage of user credentials for the
# Overseer application.
class OverseerCredentialManager:
    """
    The OverseerCredentialManager manages the input, handling, and storage of user
    credentials for the Overseer application.
    """
    def __init__(self):
        """
        Constructor for the OverseerCredentialManager class.
        It checks if the credentials are available and loads them if they are.
        If they aren't, then it asks the user to provide the required credentials.
        """
        self.check, self.cred_dict = self.credential_check()
        self.api_id = self.cred_dict["api_id"]
        self.api_hash = self.cred_dict["api_hash"]
        self.phone = self.cred_dict["phone"]
        self.username = self.cred_dict["username"]

        if not self.check:
            # Prompt the user to provide the required credentials.
            pc.printout("You do not have all required credentials saved, this application will not work\n", pc.RED)
            pc.printout("Please, provide all of the following:\n"
                        "api_id, api_hash, phone, and username or quit with Ctrl+C\n", pc.RED)
            if not self.cred_dict["api_id"]:
                self.set_api_id()
            if not self.cred_dict["api_hash"]:
                self.set_api_hash()
            if not self.cred_dict["phone"]:
                self.set_phone()
            if not self.cred_dict["username"]:
                self.set_username()

    @staticmethod
    def credential_check() -> tuple:
        """
        Checks if a credentials file exists and loads it.
        If it doesn't exist, it creates an empty credentials dictionary.
        It also verifies that each required credential exists in the dictionary.

        Returns:
        check : bool
            Indicates whether all required credentials exist.
        cred_dict : dict
            The dictionary containing the loaded or empty credentials.
        """
        if not os.path.isfile('./credentials/credentials.pkl'):
            cred_dict = {"api_id": None, "api_hash": None, "phone": None, "username": None}
            with open("./credentials/credentials.pkl", "wb") as file:
                pickle.dump(cred_dict, file)
                file.close()
                return False, cred_dict
        else:
            with open("./credentials/credentials.pkl", "rb") as file:
                cred_dict = pickle.load(file)
                file.close()
            if cred_dict["api_id"] and cred_dict["api_hash"] and cred_dict["phone"] and cred_dict["username"]:
                return True, cred_dict
            else:
                return False, cred_dict

    def set_api_id(self):
        """
        Prompts the user to enter the API ID, saves it to the credentials dictionary,
        and stores the updated dictionary in the file.
        """
        pc.printout("Please insert your api_id: \n")
        self.api_id = input()
        self.cred_dict["api_id"] = self.api_id
        with open("./credentials/credentials.pkl", "wb") as file:
            pickle.dump(self.cred_dict, file)
            file.close()

    def set_api_hash(self):
        """
        Prompts the user to enter the API Hash, saves it to the credentials dictionary,
        and stores the updated dictionary in the file.
        """
        pc.printout("Please insert your api_hash: \n")
        self.api_hash = input()
        self.cred_dict["api_hash"] = self.api_hash
        with open("./credentials/credentials.pkl", "wb") as file:
            pickle.dump(self.cred_dict, file)
            file.close()

    def set_phone(self):
        """
        Prompts the user to enter the phone number, saves it to the credentials dictionary,
        and stores the updated dictionary in the file.
        """
        pc.printout("Please insert your phone (always with international prefix): \n")
        self.phone = input()
        self.cred_dict["phone"] = self.phone
        with open("./credentials/credentials.pkl", "wb") as file:
            pickle.dump(self.cred_dict, file)
            file.close()

    def set_username(self):
        """
        Prompts the user to enter the username, saves it to the credentials dictionary,
        and stores the updated dictionary in the file.
        """
        pc.printout("Please insert your username (without the @): \n")
        self.username = input()
        self.cred_dict["username"] = self.username
        with open("./credentials/credentials.pkl", "wb") as file:
            pickle.dump(self.cred_dict, file)
            file.close()

    @staticmethod
    def retrieve_creds() -> tuple:
        """
        Retrieves the stored credentials from the file.

        Opens the pickled dictionary containing the credentials and returns the
        values of each credential (api_id, api_hash, phone and username).

        Returns
        -------
        tuple
            A tuple containing credentials in the order: api_id, api_hash, phone and username.
        """
        with open("./credentials/credentials.pkl", "rb") as file:
            cred_dict = pickle.load(file)
            file.close()
        return cred_dict["api_id"], cred_dict["api_hash"], cred_dict["phone"], cred_dict["username"]

    @staticmethod
    def print_credentials() -> None:
        """
        Prints the stored credentials to the terminal.

        Opens the pickled file and prints the stored credentials to the terminal
        in a nicely formatted manner using the printout function from the pc module,
        which prints coloured output.

        Returns
        -------
        None
        """
        with open("./credentials/credentials.pkl", "rb") as file:
            cred_dict = pickle.load(file)
            file.close()
        pc.printout("API ID: \t{}\n"
                    "API HASH: \t{}\n"
                    "PHONE NUMBER: \t{}\n"
                    "USERNAME: \t{}\n"
                    .format(cred_dict["api_id"],
                            cred_dict["api_hash"],
                            cred_dict["phone"],
                            cred_dict["username"]), pc.GREEN)
