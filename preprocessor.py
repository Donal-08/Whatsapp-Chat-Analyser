import regex as re
import pandas as pd

# chat_data is a list
def preprocess(chat_data):  

    # Define regular expressions to match different types of messages
    pattern = re.compile(r'^(\d+/\d+/\d+, \d+:\d+\s*[A|P]M)\s-\s(.+):\s(.+)$')
    link_pattern = re.compile(r'^(\d+/\d+/\d+, \d+:\d+\s*[A|P]M)\s-\s(.+?):\s?(https?://\S+)')
    image_pattern = re.compile(r'\<Media omitted\>')
    group_notification_pattern = re.compile(r'^(\d+/\d+/\d+, \d+:\d+\s*[A|P]M)\s-\s(.+?)(?::\s)?(.+)?$')

    # Parse chat data into different categories
    messages, links, images, senders, date_times, message_type = [], [], [], [],[],[]

    for line in chat_data:
        if pattern.match(line):
            message = pattern.match(line).groups()
            if "<Media omitted>" in message:
                message_type.append("image")
            else:
                message_type.append("text")
            date_times.append(message[0])
            sender = message[1].split(":")[0]
            senders.append(sender)
            messages.append(message[2])
        elif group_notification_pattern.match(line):
            message = group_notification_pattern.match(line).groups()
            date_times.append(message[0])
            senders.append('group notificaton')
            messages.append(message[1] + message[2])
            message_type.append('notification')
        if link_pattern.search(line):
            link = link_pattern.search(line).groups()
            date_times.append(link[0])
            sender = link[1].split(":")[0]
            senders.append(sender)
            links.append(link[2])
            messages.append(link[2])
            message_type.append("link")
        if image_pattern.search(line):
            images.append(image_pattern.search(line).group())



    chat_df = pd.DataFrame({'message_date': date_times ,'senders': senders, 'message':messages, 'message_type':message_type})
    chat_df["message_date"] = pd.to_datetime(chat_df["message_date"])
    chat_df.rename(columns={'message_date':'date'}, inplace=True)

    # Extract the day, month, year and other details
    chat_df['year'] = chat_df['date'].dt.year
    chat_df['month'] = chat_df['date'].dt.month_name()
    chat_df['day'] = chat_df['date'].dt.day
    chat_df['hour'] = chat_df['date'].dt.hour
    chat_df['minute'] = chat_df['date'].dt.minute
    chat_df['day_name'] = chat_df['date'].dt.day_name()
    chat_df['period'] = chat_df.apply(lambda row: str(row.hour) + '-' + str(row.hour + 1) , axis=1)

    return chat_df
