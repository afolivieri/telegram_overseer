# Telegram Overseer: User Guide

## Introduction
Welcome to the Telegram Overseer user guide! This tool is designed for easy data collection and analysis from Telegram. It's user-friendly for non-programmers, providing insights through various commands.

## Requirements:

**Python Version: Python 3.10 is required for running this version of Telegram Overseer.**

## Updates

- **02/02/2024**: Fixed a disruptive bug that caused crashes at program initialization. Apologies for any inconvenience caused.
- **05/02/2024**: Enhanced the `search_keywords` function to include context snippets in the output CSV. For every matched keyword, a snippet of text surrounding the match is provided, offering more insight into the data.
- **20/04/2024**: Added frequency calculation and CSV export for daily and weekly post frequencies. A general overview is now available in `./graphs_data_and_visualizations/frequency/general_overview/{self.now}_general.csv`.

### Version 1.01

**Release Date:** 01/02/2024

**Major Changes:**

1. **SQL Table Structure Updates:**
   - Updated the SQL database structure for improved performance and scalability. **Note:** These changes are not backward compatible with previous versions. Users are advised to set up a new database.

2. **Enhanced Keywords Search Functionality:**
   - Added a 'Keywords Search' feature that allows for case-insensitive searches of specific keywords within posts.
   - **How to Use:**
     1. Input a list of comma-separated keywords. Keywords ending with an asterisk `*` will include variations ending with up to three additional characters.
     2. Specify a start date to filter posts within the SQL database.
     3. The tool will generate and save a CSV file in `./graphs_data_and_visualizations/keywords/{current_date}` directory, capturing all posts that match the keywords and date criteria.

3. **Optional Replies Retrieval:**
   - Introduced an option to include or exclude replies in message retrievals, allowing for customized data collection.

4. **Direct Links to Messages:**
   - The SQL database now stores direct links to the original Telegram messages, facilitating easier access to source material.

5. **Linking Forwarded Messages:**
   - Forwarded messages in the database now include links to their original posts, enhancing context understanding and traceability.

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
   - Run `pip install -r requirements.txt` to install dependencies.

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
2. Run the following command: `pip install -r requirements.txt`

This will install all the necessary libraries and packages needed to run Telegram Overseer.

### Running the Script
To run the Telegram Overseer script:

1. Ensure you're in the project directory and the virtual environment is activated.
2. Execute the script using `python telegram_overseer.py`.

## Output File Structure
Telegram Overseer organizes and saves the retrieved data in a structured manner for ease of access and analysis. Below are the details of how the data is stored and the naming conventions followed:

### Data Analysis Outputs
- SQLite Database: The analyzed data is stored in a SQLite database located at `./cleaned_data/sql/overseer_target_cleaned_data.sqlite`.
- Graphs and Visualizations: The generated graphs, word clouds, and CSV files containing analysis results are stored in the `./graphs_data_and_visualizations` directory. This directory is further organized into subfolders based on the type of analysis (e.g., engagement, reactions, frequency, etc.).

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
- **retrieve_messages**: 
  - Retrieves messages, with an option to include/exclude replies. Saves data in JSON and SQLite DB.
  - The raw messages and replies retrieved from Telegram channels are saved in JSON format in the `./output` directory. This directory is organized per channel and includes subdirectories for replies and errors.
  - Messages are saved in files named `messages_data_[channel_id].json`, while replies are saved as `replies_data_[message_id].json`.
  - Errors encountered during data retrieval are logged in text files named `errors.txt` in the corresponding channel's directory.
- **delete_double_data**: Removes duplicate entries in the database.
- **full_replies_view**: Creates a view in SQLite named 'full_replies' with all messages and their replies.

### Analysis Tools
   - **engagement**: 
      - Extracts top engagement statistics and saves them in a CSV file.
      - Files related to engagement analysis are saved in the format `top_[number]_[type]_interactions.csv` within `./graphs_data_and_visualizations/engagement/[timestamp]/`.
   - **reaction_data**: 
     - Generates a CSV with a summary of all reactions per type and the top post for each reaction.
     - Files containing reaction data summaries are named `top_[number]_reactions.csv` and `top_[number]_post_for_top_[number]_reactions.csv`, located in `./graphs_data_and_visualizations/reactions/[timestamp]/`.
   - **wordclouds**: 
     - Creates two word clouds, one from target posts and another including replies.
     - Word cloud images are saved as `posts.png` and `posts_and_replies.png` in the directory `./graphs_data_and_visualizations/wordcloud/[timestamp]/`.
   - **frequency**:
     - Extracts the 24-hour and weekly frequency of posts from the targets.
     - Frequency analysis files are named as `[author]_UTC_hourly_frequency.csv` and `[author]_weekly_daily_frequency.csv`, stored in `./graphs_data_and_visualizations/frequency/[author]/[timestamp]/`.
     - Extracts the **24-hour** and **weekly frequency of posts** for each target.
     - Frequency analysis files are named `[author]_UTC_hourly_frequency.csv` for hourly data and `[author]_weekly_frequency.csv` for weekly data, stored in `./graphs_data_and_visualizations/frequency/[author]/[timestamp]/`.
     - A **general overview** file is created daily and weekly which is stored as `{self.now}_general.csv` in `./graphs_data_and_visualizations/frequency/general_overview/`.
- **keywords_search**: 
  - This function allows you to search for specific keywords within the posts. It creates a table with all posts containing the specified keywords (case insensitive).
  - Keywords can have special modifiers:
       - A single asterisk `*` at the end of a keyword includes variations of the word with up to three additional characters.
       - A double asterisk `**` at the end of a keyword extends the variation to up to six additional characters.
       - A hashtag `#` at the start of a keyword includes a numeric match of up to three digits.
       - A double hashtag `##` at the start of a keyword extends the numeric match to up to six digits.
  - Enhanced functionality now includes the option for the user to specify the context match length when searching for keywords within posts. This allows for more flexibility in analyzing text around keyword matches.
  - Upon initiating a keyword search, users are prompted to enter the desired length of text context around each keyword match. If no input is provided, the default context length of 20 characters before and after the match is used.
  - Matches are separated by "@@" to easily distinguish between multiple matches within the text column.
  - The column order has been updated to place `matched_keywords` and `context` immediately after the `text` column for more intuitive data analysis.
  - The matching posts are then saved in a CSV file named `keywords_[current_date]_[incremental_number].csv` within the `./graphs_data_and_visualizations/keywords/[current_date]/` directory. `[current_date]` is the date of the search, and `[incremental_number]` is an auto-incrementing number that ensures each search result is saved in a unique file.
  - The CSV file contains all posts that match the given keywords and date criteria, including an additional column `matched_keywords` which lists the keywords found in each post.

### Customization for Analysis
- **add_stopwords**: Adds custom stopwords for the word cloud.
- **show_stopwords**: Displays custom stopwords used in the word cloud.
- **remove_stopwords**: Removes custom stopwords from the word cloud.

## Conclusion
This guide aims to provide a smooth experience for setting up and using Telegram Overseer. If you encounter any issues or have questions, don't hesitate to contact me.
