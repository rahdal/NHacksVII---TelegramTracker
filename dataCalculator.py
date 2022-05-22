import sys
import csv
import json
from datetime import datetime

#Progress bar
from tqdm import tqdm

#Data crunching
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from functools import partial
from datetime import date
from emoji import UNICODE_EMOJI

columns = ["msg_id",
            "sender",
            "sender_id",
            "reply_to_msg_id",
            "date",
            "msg_type",
            "msg_content",
            "has_mention",
            "has_email",
            "has_phone",
            "has_hashtag",
            "is_bot_command"]

file_types = ["animation",
              "video_file",
              "video_message",
              "voice_message",
              "audio_file"]

mention_types = ["mention",
                 "mention_name"]


#Initial json file (always named result.json)
result_filepath = "JSON/result.json"

#Create new csv file for output
output_filepath = "csvFiles/output.csv"

#Load the input file
with open(result_filepath, encoding='utf8') as input_file:
    telegram_export = json.load(input_file)

#Find the name of the chat
chat_name = telegram_export['name']
print("Generating file for chat: " + chat_name)

#Find the number of messages in the chat
num_messages = len(telegram_export['messages'])

print("Found " + str(num_messages) + " messages in chat.")


output = output_filepath
with open(result_filepath, "r", encoding="utf-8") as infile:
    with open(output, "w", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, columns, dialect="unix", quoting=csv.QUOTE_NONNUMERIC)
        writer.writeheader()
        
        contents = infile.read()

        jdata = json.loads(contents)

        obj = jdata

        for message in tqdm(obj["messages"]):
            if message["type"] != "message":
                continue
            
            msg_id = message["id"]
            sender = message["from"]
            sender_id = message["from_id"]
            reply_to_msg_id = message["reply_to_message_id"] if "reply_to_message_id" in message else -1
            date = message["date"].replace("T", " ")
            dt = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
            
            msg_content = message["text"]
            msg_type = "text"
            
            if "media_type" in message:
                msg_type = message["media_type"]
                if message["media_type"] == "sticker":
                    if "sticker_emoji" in message:
                        msg_content = message["file"]
                    else:
                        msg_content = "?"
                elif message["media_type"] in file_types:
                    msg_content = message["file"]
            elif "file" in message:
                msg_type = "file"
                msg_content = message["file"]
            
            if "photo" in message:
                msg_type = "photo"
                msg_content = message["photo"]
            elif "poll" in message:
                msg_type = "poll"
                msg_content = str(message["poll"]["total_voters"])
            elif "location_information" in message:
                msg_type = "location"
                loc = message["location_information"]
                msg_content = str(loc["latitude"]) + "," + str(loc["longitude"])
            
            has_mention = 0
            has_email = 0
            has_phone = 0
            has_hashtag = 0
            is_bot_command = 0
            
            if type(msg_content) == list:
                txt_content = ""
                for part in msg_content:
                    if type(part) == str:
                        txt_content += part
                    elif type(part) == dict:
                        if part["type"] == "link":
                            msg_type = "link"
                        elif part["type"] in mention_types:
                            has_mention = 1
                        elif part["type"] == "email":
                            has_email = 1
                        elif part["type"] == "phone":
                            has_phone = 1
                        elif part["type"] == "hashtag":
                            has_hashtag = 1
                        elif part["type"] == "bot_command":
                            is_bot_command = 1
                        
                        txt_content += part["text"]
                msg_content = txt_content
            
            msg_content = msg_content.replace("\n", " ")
            
            row = {
                "msg_id"          : msg_id,
                "sender"          : sender,
                "sender_id"       : sender_id,
                "reply_to_msg_id" : reply_to_msg_id,
                "date"            : date,
                "msg_type"        : msg_type,
                "msg_content"     : msg_content,
                "has_mention"     : has_mention,
                "has_email"       : has_email,
                "has_phone"       : has_phone,
                "has_hashtag"     : has_hashtag,
                "is_bot_command"  : is_bot_command,
            }
            
            writer.writerow(row)


#Load output.csv into df
with open('csvFiles/output.csv', encoding='utf8') as input_file:
    df = pd.read_csv(input_file)
df[['sender']] = df[['sender']].fillna('Deleted Account')


# Set index to message id
msg_df = df.set_index('msg_id')
# Create a new column with the sender of what each message is replying to
msg_df['reply_to_name'] = msg_df[msg_df['reply_to_msg_id'] != -1]['reply_to_msg_id'] \
    .map(partial(msg_df['sender'].get, default=np.NaN))
# Count the amount of times each replier-sender pair occurs
commonPairings = msg_df[msg_df['reply_to_name'].notnull()] \
    .reset_index() \
    .set_index(['sender', 'reply_to_name', 'msg_id'])['reply_to_msg_id'] \
    .groupby(['sender', 'reply_to_name'], ) \
    .count() \
    .sort_values(ascending=False)
# Get top 10, format, and write to csv
reduced = commonPairings.reset_index()[:10]
reduced['Pair'] = reduced['sender'] + ' -> ' + reduced['reply_to_name']
reduced = reduced.drop(['sender', 'reply_to_name'], axis=1).rename(columns={'reply_to_msg_id': 'Messages'}, )
reduced.to_csv("csvFiles/CommonPairings.csv", index=False)




users = df['sender'].unique()

#Create a line graph showing activity of users each day
#Create new df with columns "all" then each user
#Add day column to df with just the first 10 characters of df['date']
df['day'] = df['date'].apply(lambda x: x[:10])

dailyActivity = df[['sender', 'day']].rename(columns={'day': 'Date'}) \
    .groupby(['Date']) \
    .value_counts() \
    .unstack(level=1) \
    .fillna(0) \
    .astype(int)
dailyActivity['all'] = dailyActivity.sum(axis=1)
dailyActivity = dailyActivity[['all'] + list(users)]

#Group the rows of dailyActivity by month
#If the first 7 characters of the row name are the same, then they are in the same month
#Add up the columns for all rows in the same month
dailyActivityByMonth = dailyActivity.groupby(lambda x: x[:7]).sum()

#Label index
dailyActivity.index.name = 'Date'
dailyActivityByMonth.index.name = 'Month'

dailyActivity.to_csv("csvFiles/DailyActivity.csv")
dailyActivityByMonth.to_csv("csvFiles/DailyActivityByMonth.csv")

#Calculate hourly activity
#Create new df with columns "all" then each user
hourlyActivity = pd.DataFrame(columns=['all'] + list(users))

#Add new column "time" and "hour" to df 11:19
df['time'] = df['date'].apply(lambda x: x[11:19])
df['hour'] = df['time'].apply(lambda x: int(x[:2]))

dfHourGrouped = df[['sender', 'hour']] \
    .groupby(['hour', 'sender']) \
    .value_counts() \
    .unstack(level=1) \
    .fillna(0) \
    .astype(int)
dfHourGrouped['all'] = dfHourGrouped.sum(axis=1)
dfHourGrouped = dfHourGrouped[['all'] + list(users)]

dfHourGrouped.index.name = 'Hour'
dfHourGrouped.to_csv("csvFiles/HourlyActivity.csv")



def is_emoji(s):
    return s in UNICODE_EMOJI['en']

#Add a column with the number of characters in the message
df['messageLength'] = df['msg_content'].apply(lambda x: len(str(x)))
#Add a column with the number of capital characters in each message
df['capitalLetters'] = df['msg_content'].apply(lambda x: sum(1 for c in str(x) if c.isupper()))
#Add a column with the number of emojis in each message
df['emojiCount'] = df['msg_content'].apply(lambda x: sum(1 for c in str(x) if is_emoji(c)))
#Add a column with 1 if message is all caps, 0 otherwise
df['allCaps'] = df['msg_content'].apply(lambda x: 1 if str(x).isupper() else 0)

#Make a new dataframe where each row is a user
userData = pd.DataFrame()
#Add column for num messages sent
for row in users:
    #Add column for num messages sent
    userData.loc[row, 'numMessages'] = len(df[df['sender'] == row])
    #Add column for percentage for num emojis sent
    userData.loc[row, 'emojiPercentage'] = (df[df['sender'] == row]['emojiCount'].sum() / df[df['sender'] == row]['messageLength'].sum()) * 100
    #Add column for percentage for num capital letters sent
    userData.loc[row, 'capitalLettersPercentage'] = (df[df['sender'] == row]['capitalLetters'].sum() / df[df['sender'] == row]['messageLength'].sum()) * 100
    #Add column for percentage of all caps messages
    userData.loc[row, 'allCapsPercentage'] = (df[df['sender'] == row]['allCaps'].sum() / userData['numMessages'][row]) * 100
userData.index.name = 'User'
userData.to_csv("csvFiles/UserData.csv")