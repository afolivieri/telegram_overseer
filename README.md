# Telegram Overseer: User Guide

## Introduction
Welcome to the Telegram Overseer user guide! This tool is designed for easy data collection and analysis from Telegram. It's user-friendly for non-programmers, providing insights through various commands.

## Requirements:

**Python Version: Python 3.10 is required for running this version of Telegram Overseer.**

## Updates

### Version 1.01

**Release Date:** 01/02/2024

**Major Changes:**

1. **SQL Table Structure Changes:**
   - The SQL database structure has been updated. These changes are not backward compatible with previous versions. Users are advised to start a fresh database setup to accommodate these changes.

2. **Keywords Search Functionality:**
   - A new feature, 'Keywords Search', has been added. This allows users to search for specific keywords within posts in a case-insensitive manner, enhancing the tool's analytical capabilities.

3. **Optional Replies Retrieval Flag:**
   - Users now have the option to include or exclude replies when retrieving messages. This makes the data collection process more flexible and tailored to specific analysis needs.

4. **Direct Link to Messages:**
   - The SQL database now includes direct links to the original Telegram messages. This allows for easier referencing and accessing of the source material directly from the database.

5. **Forwarded Messages Linking:**
   - For forwarded messages, links to the original posts are now included in the SQL database. This feature provides a better understanding of the message context and origin.

### Setting Up a Telegram Developer Account and Obtaining API Credentials

Before you start using Telegram Overseer, you need to set up a Telegram Developer account and obtain your API ID and API Hash. These credentials are essential for the tool to interact with Telegram’s API. Follow these steps to set up your account and get your credentials:

1. **Create a Telegram Developer Account**:
   - Visit [Telegram’s Developer Page](https://my.telegram.org).
   - Log in with your Telegram account. Ensure that the phone number you use here is the same as the one you intend to use with Telegram Overseer.

2. **Register a New Application**:
   - Once logged in, go to the 'API development tools' section.
   - Click on 'Create a new application'.
   - Fill in the required details such as the application name, short name, and URL (if any). The application name can be anything, such as "Telegram Overseer".

3. **Obtain API ID and API Hash**:
   - After registering your application, you will receive your unique `API ID` and `API Hash`.
   - Make a note of these credentials as they will be required to configure the Telegram Overseer tool.

4. **Configuring Telegram Overseer**:
   - Use the `set_api_id` and `set_api_hash` commands in Telegram Overseer to input your obtained API ID and API Hash.
   - This will allow the tool to access Telegram's API with your developer credentials.

It's important to keep your API ID and API Hash confidential. These credentials provide access to the Telegram API and should only be used with trusted applications.

## Setting Up the Environment

### Installing Python
Ensure Python is installed on your system. You can download it from the [official Python website](https://www.python.org/downloads/release/python-3100/).

#### Optional But Recommended: Setting Up PyCharm for Development

1. **Download and Install PyCharm**:
   - Visit the [PyCharm download page](https://www.jetbrains.com/pycharm/download/).
   - Choose the edition that suits your needs (Community Edition is free).
   - Follow the installation instructions for your operating system.

2. **Cloning the Repository with PyCharm**:
   - Open PyCharm and select `Get from VCS` (Version Control System).
   - Enter the URL of the Telegram Overseer Git repository.
   - Choose the directory where you want to clone the repository and click `Clone`.

3. **Setting Up the Virtual Environment**:
   - In PyCharm, go to `File > Settings > Project: Telegram Overseer > Python Interpreter`.
   - Click the gear icon and choose `Add`.
   - Select `Virtual Environment`, and ensure the `Base interpreter` points to your Python installation.
   - Choose the location for your new virtual environment within your project folder and click `OK`.

4. **Installing Dependencies in PyCharm**:
   - In the `Terminal` tab at the bottom of PyCharm, ensure you're in the project directory.
   - Activate your virtual environment (the method varies by OS).
   - Run `pip install -r requirements.txt` (or `requirements_windows.txt` for Windows) to install dependencies.

5. **Running the Script in PyCharm**:
   - In the PyCharm Project Explorer, right-click on `telegram_overseer.py`.
   - Select `Run 'telegram_overseer'` to execute the script.
   - PyCharm will automatically detect the correct Python interpreter and use the virtual environment you set up.

## Without Pycharm:
### Using Virtual Environments
Virtual environments in Python are used to manage project-specific dependencies. Here's how to set one up:

1. Open the Command Prompt or Terminal.
2. Navigate to your project directory (e.g., `cd path/to/your/project`).
3. Create a virtual environment with `python -m venv myenv`.
4. Activate the environment:
   - On Windows, use `myenv\Scripts\activate`.
   - On Linux, use `source myenv/bin/activate`.

### Installing Dependencies
After setting up and activating the virtual environment, you need to install the project dependencies.

1. Ensure you are in the project directory where the `requirements.txt` file is located.
2. Depending on your operating system, run one of the following commands:
   - On Windows: `pip install -r requirements_windows.txt`
   - On Linux: `pip install -r requirements.txt`

This will install all the necessary libraries and packages needed to run Telegram Overseer.

### Running the Script
To run the Telegram Overseer script:

1. Ensure you're in the project directory and the virtual environment is activated.
2. Execute the script using `python telegram_overseer.py`.

## Outputs and Database
The outputs generated by Telegram Overseer are saved in the same directory where the tool is cloned from Git. The data is stored in a SQLite database, which can be viewed and managed through DBeaver.

### Using DBeaver
DBeaver offers a graphical interface for database management. To use it:

1. Download DBeaver from [the DBeaver website](https://dbeaver.io/download/).
2. Install and open DBeaver.
3. To connect to the SQLite database:
   - Choose SQLite as the database.
   - Browse to the database file created by Telegram Overseer.
4. Now you can view and manage the database.

## Command Reference
The Telegram Overseer tool offers a variety of commands to manage credentials, targets, data retrieval, and analysis. Here's a comprehensive list with descriptions and usage instructions:

### General Commands
- **list**: Displays a list of all available commands.
- **quit** or **exit**: Terminates the program.

### Credential Management
- **credentials**: Displays all saved credentials or provides an option to set them if missing.
- **set_api_id**: Allows you to change the saved API ID.
- **set_api_hash**: Allows you to change the saved API HASH.
- **set_phone_number**: Updates the saved phone number. Remember to include the international prefix.
- **set_username**: Updates the saved username.

### Target Management
- **targets**: Lists all saved target groups.
- **set_targets**: Allows you to set target group(s).
- **reset_targets**: Clears all target group(s).
- **save_targets**: Saves all current targets.
- **load_targets**: Loads all saved targets.

### Date Management
- **date**: Displays the saved date.
- **set_start_date**: Sets the start date for data collection.
- **set_end_date**: Sets the end date for data collection.
- **reset_date**: Clears all saved dates.

### Data Retrieval and Cleaning
- **retrieve_messages**: Retrieves messages, with an option to include/exclude replies. Saves data in JSON and SQLite DB.
- **delete_double_data**: Removes duplicate entries in the database.
- **full_replies_view**: Creates a view in SQLite named 'full_replies' with all messages and their replies.

### Analysis Tools
- **engagement**: Extracts top engagement statistics and saves them in a CSV file.
- **reaction_data**: Generates a CSV with a summary of all reactions per type and the top post for each reaction.
- **wordclouds**: Creates two word clouds, one from target posts and another including replies.
- **frequency**: Extracts the 24-hour and weekly frequency of posts from the targets.
- **keywords_search**: This function allows you to search for specific keywords within the posts. It creates a table with all posts containing the specified keywords (case insensitive).

All the resulting data is saved as a CSV file(s) or PNG images in the graphs_data_and_visualizations directory.

### Customization for Analysis
- **add_stopwords**: Adds custom stopwords for the word cloud.
- **show_stopwords**: Displays custom stopwords used in the word cloud.
- **remove_stopwords**: Removes custom stopwords from the word cloud.

## Conclusion
This guide aims to provide a smooth experience for setting up and using Telegram Overseer. If you encounter any issues or have questions, don't hesitate to contact me.
