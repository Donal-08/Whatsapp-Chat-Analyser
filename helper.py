import pandas as pd
from wordcloud import WordCloud
import itertools
import emoji

def fetch_stats(selected_user, chat_df):

    if(selected_user == "Overall"):
        df = chat_df
    else:
        df = chat_df[chat_df["senders"] == selected_user]

    # 1. Fetch number of messages
    n_messages = df.shape[0]

    # 2. Fetch number of words
    words = []
    for message in df['message']:
        words.extend(message.split())
    n_words = len(words)

    # 3. Fetch number of medias
    n_medias = len(df[df["message_type"] == "image"])

    # 4. Fetch number of links
    n_links = len(df[df["message_type"] == "link"])

    return n_messages, n_words, n_medias, n_links


def top5_busiest_users(chat_df):
    # Messages sent by each user
    messages_by_user = chat_df['senders'].value_counts()
    top5 = messages_by_user.head()

    percent_messages_by_user = 100*(messages_by_user)/chat_df.shape[0]
    percent_messages_by_user = round(percent_messages_by_user, 2)
    percent_df = pd.DataFrame({'senders':percent_messages_by_user.index, 'percent':percent_messages_by_user.values})

    return top5, percent_df


def create_wordcloud(selected_user, chat_df):
    
    if(selected_user == "Overall"):
        df = chat_df
    else:
        df = chat_df[chat_df["senders"] == selected_user]
    
    # Remove group notifications and media omitted messages
    df = df[df['message_type'] == "text"]
    # Optional : You may choose to remove stopwords from WordCloud as well

    return df



def most_used_words(selected_user, chat_df):
    
    if selected_user != "Overall":
        chat_df = chat_df[chat_df["senders"] == selected_user]

    # Create a temp_df which removes group notifications, media omitted messages
    temp_df = chat_df[chat_df['message_type'] == "text"]
    
    # Remove Stopwords
    f = open('hinglish_stopwords.txt', 'r')
    stop_words = f.read()
    stop_words += "message"

    words = []
    for message in temp_df['message']:
        for word in message.lower().split():
            if word not in stop_words:
                if '@' not in word:
                    words.append(word)

    freq = {}
    for word in words:
        if word in freq:
            freq[word] += 1
        else:
            freq[word] = 1

    topwords = dict(sorted(freq.items(), key=lambda item: item[1], reverse=True))
    # Create dataframe from first 20 entries of the dictionary
    top20 = dict(itertools.islice(topwords.items(), 20))
    topwords_df = pd.DataFrame.from_dict(top20, orient='index')
    topwords_df.columns=['freq']   
    topwords_df

    return topwords_df
    

def extract_emojis(text):
    return ''.join(c for c in text if c in emoji.EMOJI_DATA)


def top_emojis_used(selected_user, chat_df):
    if selected_user != "Overall":
        chat_df = chat_df[chat_df["senders"] == selected_user]

    chat_df['emojis'] = chat_df['message'].apply(extract_emojis)
    emoji_series = chat_df['emojis'].value_counts()
    emoji_df = pd.DataFrame({'emoji':emoji_series.index, 'count':emoji_series.values})

    return emoji_df.drop(index=0)


def monthly_timeline(selected_user, chat_df):
    if selected_user != "Overall":
        chat_df = chat_df[chat_df["senders"] == selected_user]

    chat_df['year_month'] = chat_df.apply(lambda row: str(row.year) + '_' + row.month[:3], axis=1)       # PREPROCESSOR
    chat_series = chat_df.groupby(['year_month'])['message'].count()
    chat_df.drop('year_month', inplace=True, axis=1)                                                      # DROP
    
    temp_df = chat_series.to_frame()

    return temp_df


def daily_timeline(selected_user, chat_df):
    if selected_user != 'Overall':
        chat_df = chat_df[chat_df['user'] == selected_user]

    chat_df['only_date'] = chat_df['date'].dt.date                                   # PREPROCESSOR
    daily_timeline = chat_df.groupby('only_date').count()['message'].reset_index()
    
    chat_df.drop('only_date', inplace=True, axis=1)                                   # DROP

    return daily_timeline


def week_activity_map(selected_user, chat_df):
    if selected_user != 'Overall':
        chat_df = chat_df[chat_df['user'] == selected_user]

    chat_df['day_name'] = chat_df['date'].dt.day_name()                 # Preprocessor
    week_activity_series = chat_df['day_name'].value_counts()
    
    return week_activity_series


def month_activity_map(selected_user, chat_df):
    if selected_user != 'Overall':
        chat_df = chat_df[chat_df['user'] == selected_user]

    month_activity_series = chat_df['month'].value_counts()
    
    return month_activity_series


def activity_heatmap(selected_user, chat_df):
    if selected_user != 'Overall':
        chat_df = chat_df[chat_df['user'] == selected_user]

    pivot = pd.pivot_table(chat_df, index='day_name', columns='period', values='message', aggfunc='count').fillna(0)
    column_order = sorted(pivot.columns, key=lambda x: int(x.split('-')[0]))
    pivot = pivot[column_order]

    return pivot