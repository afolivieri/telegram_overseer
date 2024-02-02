import pandas as pd
import json
import os
import re
import sqlite3
import pickle
import numpy as np
import pandas.errors
from tqdm import tqdm
import src.printcolors as pc
from tzlocal import get_localzone_name
from datetime import datetime
from pytz import timezone, utc
from stop_words import get_stop_words
from wordcloud import WordCloud
# from src.credential_handler import OverseerCredentialManager
# from telethon import TelegramClient


class CleanAndSave:
    """
    Class for cleaning and saving the scraped data from Telegram.
    """
    # Get local timezone
    TZ = get_localzone_name()
    # Gets current time in the local timezone
    now = timezone(TZ).localize(datetime.replace(datetime.today())).astimezone(utc).strftime("%Y_%m_%d_%H_%M_%S")
    # Initializes some variables
    already_cleaned = []
    errors = ""
    # Defines the columns in the SQLite database
    post_columns = "channel_id INTEGER, author TEXT, message_id INTEGER, date TEXT, text BLOB, " \
                   "media_type TEXT, views INTEGER, forwards INTEGER, edit TEXT, post_url TEXT, forwarded_from TEXT"

    replies_columns = "channel_id INTEGER, message_id INTEGER, date TEXT, text BLOB, " \
                      "edit TEXT, reactions BLOB"

    dbs = ["posts", "replies"]
    columns = [post_columns, replies_columns]

    def __init__(self):
        # Create directories if they don't exist
        try:
            os.makedirs("./cleaned_data/sql")
        except FileExistsError:
            pass
        try:
            os.makedirs("./graphs_data_and_visualizations")
        except FileExistsError:
            pass
        # Connect to SQLite and set up custom collation
        self.conn = sqlite3.connect("./cleaned_data/sql/overseer_target_cleaned_data.sqlite")
        self.c = self.conn.cursor()
        # Creates tables in the SQLite database if they don't exist already
        for db, cols in zip(self.dbs, self.columns):
            self.c.execute("CREATE TABLE IF NOT EXISTS {} ({});".format(db, cols))
            self.conn.commit()
    """
        self.client_clean_and_save = None

    async def initialize_client(self):

        if self.client_clean_and_save is None:  # Check if client is already initialized
            self.api_id, self.api_hash, self.phone, self.username = OverseerCredentialManager().retrieve_creds()
            self.client_clean_and_save = TelegramClient(self.username, api_id=self.api_id, api_hash=self.api_hash)
            await self.client_clean_and_save.connect()
"""
    @staticmethod
    def extract_data(data, *args) -> tuple:
        """
        Extracts the needed data from the given data args.

        Parameters:
        data (list): The list of data to be extracted.
        *args: Variable length argument list of the details to be extracted.

        Returns:
        tuple: The data tuple extracted from the given data
        """
        # Try to extract data
        try:
            for x in args:
                if "media" not in x:
                    data = data[x]
                else:
                    try:
                        data = data["media"][list(data["media"].keys())[1]]["_"]
                    except TypeError: # Return NaN for invalid data
                        data = np.nan
                    except AttributeError: # Return NaN for invalid data
                        data = np.nan
                    except IndexError: # Return NaN for invalid data
                        data = np.nan
            return data
        except TypeError:
            return np.nan
        except KeyError:
            return np.nan

    def load_cleaned_file(self) -> None:
        """
        Loads the cleaned file, if exists.
        """
        if os.path.exists("./cleaned_data/already_cleaned.pkl"):
            with open("./cleaned_data/already_cleaned.pk", "rb") as file:
                self.already_cleaned = pickle.load(file)

    @staticmethod
    def post_reaction_clean_and_save(reactions, channel_id, message_id) -> pd.DataFrame:
        """
        Cleans and saves the post reactions.

        Parameters:
        reactions (list): The list of reactions.
        channel_id (int): The id of the channel.
        message_id (int): The id of the message.

        Returns:
        pd.DataFrame: The cleaned and saved dataframe of post reactions.
        """
        reaction_dict = {"channel_id": [], "message_id": [], "total": [0]}
        if isinstance(reactions, float):
            reaction_dict["channel_id"].append(channel_id)
            reaction_dict["message_id"].append(message_id)
            reaction_df = pd.DataFrame(reaction_dict)
        else:
            for reaction in reactions:
                reaction_dict[reaction["reaction"]] = []
                reaction_dict[reaction["reaction"]].append(reaction["count"])
            reaction_dict["channel_id"].append(channel_id)
            reaction_dict["message_id"].append(message_id)
            reaction_df = pd.DataFrame(reaction_dict)
            total = reaction_df.drop(["channel_id", "message_id", "total"], axis=1).sum(axis=1)
            reaction_df["total"] = total
        return reaction_df

    async def get_original_url_if_forwarded(self, post, client) -> str:
        """
        Processes and saves replies data into the SQLite database.

        Parameters:
        filepath (str): Path to the file containing replies data.
        ch_id (str): Channel ID of the Telegram channel.
        post_id (str): Post ID to which the replies are associated.

        Returns:
        None: The function doesn't return anything but saves data to the SQLite database.
        """
        from_data = self.extract_data(post, "fwd_from")
        if from_data is not None and (not isinstance(from_data, float) or from_data == from_data):
            from_id = self.extract_data(from_data, "from_id")
            message_id = self.extract_data(from_data, "channel_post")
            channel_id = self.extract_data(from_id, "channel_id")
            if not client.is_connected():
                await client.connect()
            try:
                entity = await client.get_entity(channel_id)
                channel_name = entity.username
                original_url = "https://t.me/{}/{}".format(channel_name, message_id)
            except ValueError:
                original_url = "channel name not found"
        else:
            original_url = "not a forwarded post"
        return original_url

    async def post_clean_and_save(self, filepath, author, ch_id, client) -> None:
        """
        This function opens the provided JSON file, loads its content, and extracts the necessary post
        data (including text, views, edit date, media type, and others). It also processes the post's reactions
        using the `post_reaction_clean_and_save` method. It then adds these data to the "Posts" SQLite database table.

        Parameters:
        filepath (str): The filepath of the post data JSON file.
        author (str): The author of the Telegram channel.
        ch_id (str) : The id of the Telegram channel.
        """
        with open(filepath, "r") as json_data:
            data = json.load(json_data)
        # If the data is empty, we don't need to proceed
        if not data:
            pass
        else:
            # If data exists, process each entry and extract necessary information
            data_dict = {"channel_id": [], "author": [], "message_id": [], "date": [], "text": [], "media_type": [],
                         "views": [], "forwards": [], "edit": [], "post_url": [], "forwarded_from": []}
            reaction_df = pd.DataFrame({})
            for post in data:
                data_dict["channel_id"].append(ch_id)
                data_dict["author"].append(author)
                msg_id = self.extract_data(post, "id")
                data_dict["message_id"].append(msg_id)
                data_dict["date"].append(self.extract_data(post, "date"))
                data_dict["text"].append(self.extract_data(post, "message"))
                data_dict["media_type"].append(self.extract_data(post, "media"))
                data_dict["views"].append(self.extract_data(post, "views"))
                data_dict["forwards"].append(self.extract_data(post, "forwards"))
                data_dict["edit"].append(self.extract_data(post, "edit_date"))
                data_dict["post_url"].append("https://t.me/{}/{}".format(author, msg_id))
                data_dict["forwarded_from"].append(await self.get_original_url_if_forwarded(post, client))
                reactions = self.extract_data(post, "reactions", "results")
                reaction_cleaned = self.post_reaction_clean_and_save(reactions, ch_id, msg_id)
                reaction_df = pd.concat([reaction_df, reaction_cleaned], axis=0, ignore_index=True)
            post_data = pd.DataFrame.from_dict(data_dict)
            post_data.to_sql("posts", self.conn, if_exists="append", index=False)
            try:
                main_df = pd.read_sql("SELECT *  FROM post_reaction_table", self.conn)
                reaction_df = pd.concat([main_df, reaction_df], axis=0, ignore_index=True)
                reaction_df.to_sql("post_reaction_table", self.conn, if_exists='replace', index=False)
            except pandas.errors.DatabaseError:
                reaction_df.to_sql("post_reaction_table", self.conn, index=False)

    def replies_clean_and_save(self, filepath, ch_id, post_id) -> None:
        """
        This function opens the provided JSON file, loads its content and extracts the necessary replies data.
        It then adds these data to the "Replies" SQLite database table.

        Parameters:
        filepath (str): The filepath of the replies data JSON file.
        ch_id (str): The id of the Telegram channel.
        post_id (str): The id of the post that the replies are associated with.
        """
        with open(filepath, "r") as json_data:
            data = json.load(json_data)
        # If the data is empty, do nothing
        if not data:
            pass
        else:
            # If data exists, process each entry
            data_dict = {"channel_id": [], "message_id": [], "date": [], "text": [],
                         "edit": [], "reactions": []}
            for reply in data:
                data_dict["channel_id"].append(ch_id)
                data_dict["message_id"].append(post_id)
                # Retrieve each necessary field with error handling
                data_dict["date"].append(self.extract_data(reply, "date"))
                data_dict["text"].append(self.extract_data(reply, "message"))
                data_dict["edit"].append(self.extract_data(reply, "edit_date"))
                reactions = self.extract_data(reply, "reactions", "results")
                if isinstance(reactions, float):
                    data_dict["reactions"].append(reactions)
                else:
                    reactions_dict = {}
                    for reaction in reactions:
                        reactions_dict[reaction["reaction"]] = reaction["count"]
                    reactions_dict["total"] = sum(reactions_dict.values())
                    data_dict["reactions"].append(reactions_dict)
            replies_data = pd.DataFrame.from_dict(data_dict)
            replies_data["reactions"] = replies_data["reactions"].astype("str")
            replies_data.to_sql("replies", self.conn, if_exists="append", index=False)

    async def cleaning_process(self, client) -> None:
        """
        Drives the data cleaning process across all relevant files in the output directory.

        Returns:
        None: The function doesn't return anything but performs data cleaning and saving.
        """
        self.load_cleaned_file()
        cleaned = []
        for root, dirs, files in tqdm(os.walk("./output"),
                                      leave=False,
                                      bar_format="{desc:<33.33}{percentage:3.0f}%|{bar:50}{r_bar}",
                                      desc="Cleaning Data"
                                      ):
            if files:
                for file in files:
                    filepath = os.path.join(root, file)
                    if filepath in self.already_cleaned:
                        pass
                    elif "errors" in filepath:
                        with open(filepath, "r") as text:
                            data = text.read()
                        self.errors = data.split(":")[-1].rstrip().lstrip().replace(" ", ", ")
                        cleaned.append(filepath)
                    else:
                        channel_or_reply_id = str(file).split("_")[-1].split(".")[0]
                        if "replies_data" in filepath:
                            channel_id = os.path.split(filepath)[0].split("replies_")[1]
                            self.replies_clean_and_save(filepath, channel_id, channel_or_reply_id)
                        else:
                            author = os.path.split(os.path.split(root)[0])[1].replace("channel_name_", "")
                            #await self.initialize_client()
                            await self.post_clean_and_save(filepath, author, channel_or_reply_id, client)
                            #await self.client_clean_and_save.disconnect()
                            self.update_with_errors(self.errors, channel_or_reply_id)
                        cleaned.append(filepath)
        self.already_cleaned.extend(cleaned)
        with open("./cleaned_data/already_cleaned.pk", "wb") as file:
            pickle.dump(self.already_cleaned, file)

    def create_full_replies_view(self):
        """
        This function creates a SQL view named "full_replies" that unifies posts and replies data for
        easier data handling and retrieval.
        """
        self.c.execute("DROP VIEW IF EXISTS full_replies")
        self.conn.commit()
        self.c.execute("CREATE VIEW full_replies "
                       "AS "
                       "SELECT p.channel_id, p.author, p.message_id, p.date, p.text AS original_text, p.views, "
                       "r.text AS reply_text, r.date AS reply_date, r.message_id AS reply_to_message_id, r.channel_id AS reply_to_channel_id "
                       "FROM posts AS p "
                       "LEFT JOIN replies AS r "
                       "USING(channel_id, message_id) "
                       "UNION ALL "
                       "SELECT p.channel_id, p.author, p.message_id, p.date, p.text AS original_text, p.views, "
                       "r.text AS reply_text, r.date AS reply_date, r.message_id AS reply_to_message_id, r.channel_id AS reply_to_channel_id "
                       "FROM replies AS r "
                       "LEFT JOIN posts AS p "
                       "USING(channel_id, message_id) "
                       "WHERE p.channel_id ISNULL")
        self.conn.commit()

    def clean_sql_tables(self) -> None:
        """
        This function removes duplicate entries from the "posts", "replies", and "post_reaction_table"
        SQLite tables and then refreshes the "full_replies" SQL view.
        """
        self.c.execute("DROP VIEW IF EXISTS full_replies")
        self.conn.commit()
        for table in ("posts", "replies", "post_reaction_table"):
            self.c.execute("CREATE TABLE temp_{} AS SELECT DISTINCT * FROM {}".format(table, table))
            self.c.execute("DROP TABLE {}".format(table))
            self.c.execute("ALTER TABLE temp_{} RENAME TO {}".format(table, table))
            self.c.execute("DROP TABLE IF EXISTS temp_{}".format(table))
            self.conn.commit()
        self.create_full_replies_view()

    def update_with_errors(self, errors, channel_id) -> None:
        """
    This method updates posts in the database that have no text and are potentially deleted or
    simply contain media with a placeholder string.

    Parameters:
    errors (str): A string of concatenated message IDs from the post cleaning function
    where an error occurred potentially due to the post being deleted or only containing media.
    channel_id (str): The ID of the Telegram channel.
    """
        self.c.execute("UPDATE posts SET text = 'Message with no text or replies, could be deleted or just media' "
                       "WHERE (text = '' AND message_id IN ({}) AND channel_id IS {})".format(errors, channel_id))
        self.conn.commit()
        self.errors = ""

    def engagement(self) -> None:
        """
        This function calculates the engagement rate for the posts in the Telegram channel.
        Engagement rate is calculated by counting the number of views, likes, and comments
        on each post and dividing it by the total followers of the channel.
        The results are then saved to a new SQLite database table called "engagement".
        """
        pc.printout(
            "This is a sum of reactions, the output will show a table with the first X posts of the targets and by target\n",
            pc.CYAN)
        pc.printout("Number of posts to show:\n", pc.CYAN)
        number_of_tweets = input()
        try:
            os.makedirs("./graphs_data_and_visualizations/engagement/{}".format(self.now))
        except FileExistsError:
            pass
        sql = "SELECT p.author, p.date, p.text, p.media_type, p.views, p.forwards, p.edit, " \
              "prt.total AS total_reaction_count FROM posts p " \
              "JOIN post_reaction_table prt " \
              "ON (p.channel_id = prt.channel_id AND p.message_id = prt.message_id) " \
              "ORDER BY total DESC " \
              "LIMIT {};".format(number_of_tweets)
        global_df = pd.read_sql_query(sql=sql, con=self.conn)
        global_df["total_reaction_count"] = global_df["total_reaction_count"].astype(int)
        global_df.to_csv("./graphs_data_and_visualizations/engagement/{}/top_{}_global_interactions.csv"
                         .format(self.now, number_of_tweets), index=False, encoding='utf-8')
        sql_1 = "SELECT DISTINCT author FROM posts;"
        distinct_authors_df = pd.read_sql_query(sql=sql_1, con=self.conn)
        for author in distinct_authors_df["author"].tolist():
            sql_2 = "SELECT p.author, p.date, p.text, p.media_type, p.views, p.forwards, p.edit, " \
                    "prt.total AS total_reaction_count FROM posts p " \
                    "JOIN post_reaction_table prt " \
                    "ON (p.channel_id = prt.channel_id AND p.message_id = prt.message_id) " \
                    "WHERE author = '{}' " \
                    "ORDER BY prt.total DESC, p.views DESC " \
                    "LIMIT {};".format(author, number_of_tweets)
            author_df = pd.read_sql_query(sql=sql_2, con=self.conn)
            author_df["total_reaction_count"] = author_df["total_reaction_count"].astype(int)
            author_df.to_csv("./graphs_data_and_visualizations/engagement/{}/top_{}_by_{}_interactions.csv"
                             .format(self.now, number_of_tweets, author), index=False, encoding='utf-8')
        pc.printout("Done!\n", pc.CYAN)

    def reaction_data(self) ->None:
        """
        This function loads the reactions data and saves it into a new SQLite database
        table called "reaction_analysis". The reaction data shows how many of each reaction
        was used in the channel.
        """
        pc.printout("This is a sum of all reaction per reaction type. It also output the top post per top reaction\n",
                    pc.CYAN)
        pc.printout("Number of top reaction to consider:\n", pc.CYAN)
        number_of_reactions = input()
        pc.printout("Number of post per reaction:\n", pc.CYAN)
        post_per_reaction = input()
        try:
            os.makedirs("./graphs_data_and_visualizations/reactions/{}".format(self.now))
        except FileExistsError:
            pass
        reaction_table_sql = "SELECT * FROM post_reaction_table prt;"
        reaction_df = pd.read_sql_query(sql=reaction_table_sql, con=self.conn)
        reaction_df.drop(["channel_id", "message_id", "total"], axis=1, inplace=True)
        reaction_df = pd.DataFrame(reaction_df.sum())
        reaction_df.reset_index(inplace=True)
        reaction_df.columns = ["emoji", "total"]
        reaction_df.sort_values(by="total", ascending=False, inplace=True)
        reaction_df = reaction_df.head(int(number_of_reactions))
        reaction_df.to_csv("./graphs_data_and_visualizations/reactions/{}/top_{}_reactions.csv"
                           .format(self.now, number_of_reactions), index=False, encoding='utf-8')
        merged_emoji_df = pd.DataFrame(columns=["text", "author", "emoji", "total"])
        for emoji in reaction_df["emoji"]:
            emoji_sql = "SELECT p.text, p.author, p.media_type, p.date, prt.{}  FROM post_reaction_table prt " \
                        "JOIN posts p ON  (p.channel_id = prt.channel_id AND p.message_id = prt.message_id) " \
                        "ORDER BY prt.{} DESC " \
                        "LIMIT {};".format(emoji, emoji, post_per_reaction)
            emoji_df = pd.read_sql_query(sql=emoji_sql, con=self.conn)
            emoji_df["emoji"] = emoji
            emoji_df.rename(columns={emoji: "total"}, inplace=True)
            merged_emoji_df = pd.concat([merged_emoji_df, emoji_df], ignore_index=True)
        merged_emoji_df.to_csv("./graphs_data_and_visualizations/reactions/{}/top_{}_post_for_top_{}_reactions.csv"
                               .format(self.now, post_per_reaction, number_of_reactions), index=False, encoding='utf-8')
        pc.printout("Done!\n", pc.CYAN)

    @staticmethod
    def add_stopwords() ->None:
        """
        This function is used to add custom stopwords to the text analysis process.
        """
        pc.printout("Add stopwords for the wordcloud, separate them with a whitespace\n", pc.CYAN)
        try:
            os.makedirs("./graphs_data_and_visualizations/wordcloud/custom_stopwords")
        except FileExistsError:
            pass
        stop_words = input()
        stop_words_list = stop_words.split(" ")
        if not os.path.isfile("./graphs_data_and_visualizations/wordcloud/custom_stopwords/stopwords_list.pkl"):
            with open("./graphs_data_and_visualizations/wordcloud/custom_stopwords/stopwords_list.pkl", "wb") as file:
                pickle.dump(sorted(stop_words_list), file)
        else:
            with open("./graphs_data_and_visualizations/wordcloud/custom_stopwords/stopwords_list.pkl", "rb") as file:
                old_stop_words_list = pickle.load(file)
            new_stop_words = old_stop_words_list + stop_words_list
            with open("./graphs_data_and_visualizations/wordcloud/custom_stopwords/stopwords_list.pkl", "wb") as file:
                pickle.dump(sorted(new_stop_words), file)

    @staticmethod
    def show_custom_stopwords() ->None:
        """
        This function shows the current list of custom stopwords.
        """
        if not os.path.isfile("./graphs_data_and_visualizations/wordcloud/custom_stopwords/stopwords_list.pkl"):
            pc.printout("No custom stopwords are saved\n", pc.CYAN)
        else:
            with open("./graphs_data_and_visualizations/wordcloud/custom_stopwords/stopwords_list.pkl", "rb") as file:
                stop_words_list = pickle.load(file)
            for word in stop_words_list:
                print(word, end=", ", flush=True)
            print("\n")

    @staticmethod
    def remove_custom_stopwords() ->None:
        """
        This function removes words from the custom stopwords list.
        """
        pc.printout("Remove stopwords from the custom stopword list, separate them with a whitespace\n", pc.CYAN)
        try:
            os.makedirs("./graphs_data_and_visualizations/wordcloud/custom_stopwords")
        except FileExistsError:
            pass
        stop_words_to_remove = input()
        stop_words_to_remove_list = stop_words_to_remove.split(" ")
        if not os.path.isfile('./graphs_data_and_visualizations/wordcloud/custom_stopwords/stopwords_list.pkl'):
            pc.printout("No custom stopwords are saved\n", pc.CYAN)
        else:
            with open("./graphs_data_and_visualizations/wordcloud/custom_stopwords/stopwords_list.pkl", "rb") as file:
                stop_words_list = pickle.load(file)
            for word in stop_words_to_remove_list:
                stop_words_list.remove(word)
            with open("./graphs_data_and_visualizations/wordcloud/custom_stopwords/stopwords_list.pkl", "wb") as file:
                pickle.dump(sorted(stop_words_list), file)

    def wordclouds(self) ->None:
        """
        This function creates two Wordcloud images: one from just the author's posts and another from
        the author's posts and the replies together. It first sets up a directory for storing the Wordcloud
        images. Then it checks if a custom stopwords list exists and loads it if available. After that,
        it queries the database and constructs wordlists for generating the Wordclouds.

        Stopwords used include English, Italian, Russian, and Ukrainian language stopwords, internet-related terms,
        and the channel name. Custom stopwords are also used if available.

        Wordcloud images are then generated and saved in the previously created directory.
        """
        pc.printout("This will create two Wordclouds, one from just the authors posts, another form those and the replies together\n",
                    pc.CYAN)
        pc.printout("Stopwords are in English, Italian, Russian, and Ukrainian internet related (www, https, com) and channel name\n",
                    pc.CYAN)
        try:
            os.makedirs("./graphs_data_and_visualizations/wordcloud/{}".format(self.now))
        except FileExistsError:
            pass
        if os.path.isfile("./graphs_data_and_visualizations/wordcloud/custom_stopwords/stopwords_list.pkl"):
            with open("./graphs_data_and_visualizations/wordcloud/custom_stopwords/stopwords_list.pkl", "rb") as file:
                custom_stopwords = pickle.load(file)
        else:
            custom_stopwords = [""]
        wordcloud_sql_1 = "SELECT text FROM posts;"
        wordcloud_sql_2 = "SELECT text FROM replies;"
        stopword_query_1 = "SELECT DISTINCT author FROM posts;"
        wordcloud_df_1 = pd.read_sql_query(sql=wordcloud_sql_1, con=self.conn)
        wordcloud_df_2 = pd.read_sql_query(sql=wordcloud_sql_2, con=self.conn)
        stopword_df_1 = pd.read_sql_query(sql=stopword_query_1, con=self.conn)
        wordlist_1 = " ".join(filter(None, (post for post in wordcloud_df_1.text.to_list())))
        wordlist_2 = " ".join(filter(None, (post for post in wordcloud_df_2.text.to_list())))
        wordlist_merged = wordlist_1 + wordlist_2
        stopwords = get_stop_words("italian") + \
                    get_stop_words("english") + \
                    get_stop_words("russian") + \
                    get_stop_words("ukrainian") + \
                    "Message with no text or replies, could be deleted or just media".split(" ") + \
                    "canale www https portale web com t ru it".split(" ") + \
                    stopword_df_1.author.to_list() + \
                    custom_stopwords
        wordimg = WordCloud(stopwords=stopwords, background_color="white", max_words=150, width=1600, height=800)\
            .generate(wordlist_1)
        wordimg.to_file("./graphs_data_and_visualizations/wordcloud/{}/posts.png".format(self.now))
        wordimg = WordCloud(stopwords=stopwords, background_color="white", max_words=150, width=1600, height=800)\
            .generate(wordlist_merged)
        wordimg.to_file("./graphs_data_and_visualizations/wordcloud/{}/posts_and_replies.png".format(self.now))
        pc.printout("Done!\n", pc.CYAN)

    @staticmethod
    def list_count(a_list, colname) ->pd.DataFrame:
        """
        Counts the occurrence of each unique item in a_list

        Parameters:
        a_list (list): The list of items.
        colname (str): The name of the item attribute.

        Returns:
        pd.DataFrame: The DataFrame of items and their frequencies sorted in descending order.
        """
        if a_list is None:
            a_list = ["No {}".format(colname)]
        count_dict = {}
        for i in a_list:
            if i in count_dict.keys():
                count_dict[i] += 1
            else:
                count_dict[i] = 1
        count_df = pd.DataFrame.from_dict([count_dict]).T
        count_df.reset_index(inplace=True)
        count_df.columns = [colname, "occurrencies"]
        count_df.sort_values(by="occurrencies", ascending=False, inplace=True)
        return count_df

    @staticmethod
    def fill_df(df, type, colname) ->pd.DataFrame:
        """
        Fills a DataFrame with missing hours or weekdays and sorts it either by daily hours or weekly days.

        Parameters:
        df (pd.DataFrame): The DataFrame to fill.
        type (str): The type of fill - 'daily' for hours, 'weekly' for weekdays.
        colname (str): The column name to operate on.

        Returns:
        pd.DataFrame: The filled and sorted DataFrame.
        """
        if type == "daily":
            for h in ["00", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12",
                      "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23"]:
                if h in df[colname].values:
                    pass
                else:
                    df.loc[len(df)] = [h, 0]
            df.sort_values(by=colname, inplace=True)
            return df
        else:
            weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            df[colname] = df[colname].astype(str)
            for d in weekdays:
                if d in df[colname].values:
                    pass
                else:
                    df.loc[len(df)] = [d, 0]
            df = df.set_index(colname)
            df_sorted = df.loc[weekdays]
            df_sorted.reset_index(inplace=True)
            return df_sorted

    def frequency(self) ->None:
        """
        This function creates two frequency tables for each author: one with daily frequencies and one with weekly frequencies.
        It fetches the post data for each author and extracts the date and time information.
        It saves these tables in .csv format in the directory './graphs_data_and_visualizations/frequency/{author}/{self.now}/'.
        """
        pc.printout("This will create two tables for each target containing the daily and weekly frequency of posts\n"
                    , pc.CYAN)
        sql = "SELECT DISTINCT author, channel_id FROM posts p;"
        distinct_authors_df = pd.read_sql_query(sql=sql, con=self.conn)
        for author in distinct_authors_df["author"].tolist():
            try:
                os.makedirs("./graphs_data_and_visualizations/frequency/{}/{}".format(author, self.now))
            except FileExistsError:
                pass
            frequency_sql = "SELECT p.date FROM posts p " \
                            "WHERE author = '{}';".format(author)
            frequency_df = pd.read_sql_query(sql=frequency_sql, con=self.conn, parse_dates=["date"])
            frequency_df["24_H"] = frequency_df["date"].dt.strftime('%H')
            frequency_df["weekly"] = frequency_df["date"].dt.strftime('%A')
            HH_list = frequency_df["24_H"].astype(str).tolist()
            AA_list = frequency_df["weekly"].astype(str).tolist()
            HH_df = self.list_count(HH_list, colname="24_hours_UTC_frequency")
            AA_df = self.list_count(AA_list, colname="weekly_frequency")
            HH_df = self.fill_df(HH_df, "daily", "24_hours_UTC_frequency")
            AA_df = self.fill_df(AA_df, "weekly", "weekly_frequency")
            HH_df.to_csv("./graphs_data_and_visualizations/frequency/{}/{}/{}_UTC_hourly_frequency.csv"
                         .format(author, self.now, author), index=False)
            AA_df.to_csv("./graphs_data_and_visualizations/frequency/{}/{}/{}_weekly_daily_frequency.csv"
                         .format(author, self.now, author), index=False)
        pc.printout("Done!\n", pc.CYAN)

    def search_keywords(self) -> None:
        """
        Creates a table with all posts containing specified keywords.

        Parameters:
        None: The function takes input from the user.

        Returns:
        None: The function doesn't return anything but saves the resulting data as a CSV.
        """
        pc.printout("This will create a table with all the posts with the matching keywords (case insensitive)\n", pc.CYAN)
        pc.printout("Please, give me a list of comma separated words you want to search\n", pc.CYAN)
        words = input()
        wordlist = [word.strip().casefold() for word in words.split(",")]

        pc.printout("Please, give me a start date to filter the SQL database, the format should be dd/mm/yyyy\n", pc.CYAN)
        date_start = input()
        date_start = datetime.strptime(date_start, '%d/%m/%Y').strftime('%Y-%m-%d')
        try:
            os.makedirs("./graphs_data_and_visualizations/keywords/{}".format(self.now))
        except FileExistsError:
            pass
        keyword_sql = ("SELECT * from posts p "
                       "WHERE date >= '{}';").format(date_start)
        all_posts_df = pd.read_sql_query(sql=keyword_sql, con=self.conn)
        # Pattern to match any number of emojis
        emoji_pattern = r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]'
        # Combine emoji pattern with each word in the wordlist
        combined_patterns = [f'(?:{emoji_pattern})*{word}' for word in wordlist]
        pattern = '|'.join(combined_patterns)
        print(pattern)
        matching_posts_df = all_posts_df[all_posts_df['text'].str.contains(pattern, flags=re.IGNORECASE, regex=True, na=False)]
        print(matching_posts_df)
        matching_posts_df.to_csv("./graphs_data_and_visualizations/keywords/{}/keywords.csv".format(self.now), index=False)
