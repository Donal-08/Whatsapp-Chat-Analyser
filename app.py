import streamlit as st
from preprocessor import preprocess
from helper import fetch_stats, top5_busiest_users, create_wordcloud, most_used_words, top_emojis_used, monthly_timeline, daily_timeline, week_activity_map, month_activity_map, activity_heatmap
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
from wordcloud import WordCloud, STOPWORDS

N_EMOJIS_TO_DISPLAY = 5


st.sidebar.title("Whatsapp Chat Analyser")

# Set app title
st.title("WhatsApp Chat Analyzer")

# Add file uploader to sidebar
st.sidebar.title("Upload chat file")
file = st.sidebar.file_uploader("Choose a WhatsApp chat file (.txt)", type="txt")

# Check if file has been uploaded
if file is not None:
    bytes_data = file.getvalue()
    data = bytes_data.decode("utf-8")
    # Convert the data(string) to a list of strings
    chat_data = data.split('\n')
    # Convert list of strings to a DF using preprocess function of preprocessor module
    chat_df = preprocess(chat_data)  
    # Display number of messages, media, and links
    num_messages = len(chat_df)

    st.write("## Chat statistics") 
    st.dataframe(chat_df)

    # Fetch all unique senders
    sender_list = chat_df['senders'].unique().tolist()
    sender_list.sort()
    sender_list.remove('group notificaton')
    sender_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("Show Analysis wrt", sender_list)

    if st.sidebar.button("Show Analysis"):

        ######################    Stats Area    ######################
        n_messages, n_words, n_medias, n_links = fetch_stats(selected_user, chat_df)
        st.title("Top Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.header("Total Messages")
            st.subheader(n_messages)

        with col2:
            st.header("Total Words")
            st.subheader(n_words)

        with col3:
            st.header("Total Links")
            st.subheader(n_links)

        with col4:
            st.header("Medias Shared")
            st.subheader(n_medias)

        #________________________________ Time Related Analysis ________________________________#

        st.title("TIME RELATED ANALYSIS")
        # A) MONTHLY TIMELINE :
        temp_df = monthly_timeline(selected_user, chat_df)

        st.header("Monthly Timeline")
        f, ax = plt.subplots(figsize=(6, 6))
        sns.set_palette("hls", 8)
        sns.lineplot(temp_df, markers=True)
        f.autofmt_xdate(rotation=45)
        ax.set_xlabel("Year-Month", size = 16)
        ax.set_ylabel("No. of messages", size = 16)
        ax.set_title('Monthly Timeline', size = 20)
        ax.legend(["Message count"])

        st.pyplot(f)
        
        # B) DAILY TIMELINE :
        daily_timeline = daily_timeline(selected_user, chat_df)

        st.header("Daily Timeline")
        f, ax = plt.subplots()
        ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='black')
        plt.xticks(rotation='vertical')
        st.pyplot(f)



        # C) WEEK ACTIVITY ANALYSIS :
        st.header("Activity Map")
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Most Busy Day Analysis")
            week_activity_series = week_activity_map(selected_user, chat_df)
            f,ax = plt.subplots()
            ax.bar(week_activity_series.index, week_activity_series.values, color='red')
            plt.xticks(rotation='vertical')
            st.pyplot(f)

        with col2:
            st.subheader("Most Busy Month Analysis")
            month_activity_series = month_activity_map(selected_user, chat_df)
            f,ax = plt.subplots()
            ax.bar(month_activity_series.index, month_activity_series.values, color='orange')
            plt.xticks(rotation='vertical')
            st.pyplot(f)


        # D) Activity Heatmap
        st.header("Activity Heatmap")

        pivot = activity_heatmap(selected_user, chat_df)
        # Create a heatmap to visualize the pivot table
        f, ax = plt.subplots(figsize=(12,8))
        sns.heatmap(pivot, fmt='.0f')

        ax.set_xlabel('Hour of Day', size = 16)
        ax.set_ylabel("Day of Week", size = 16)
        st.pyplot(f)


        ################ Finding the busiest users in the group(GROUP LEVEL) ###############
        
        sns.set_theme(style="whitegrid")
        font_prop = font_manager.FontProperties(size=18)

        if selected_user == "Overall":
            st.title("Most Active Users & Contributions")
            top5, percent_messages_df = top5_busiest_users(chat_df)
            
            f, ax = plt.subplots(figsize=(6, 6))

            col1, col2 = st.columns(2)

            with col1: 
                sns.barplot(x=top5.values, y=top5.index).set_title("Most Active Users", fontdict={'size':20, 'weight':'bold'})
                plt.rc('axes', labelsize=30)    
                plt.xlabel("No. of messages ->", fontproperties=font_prop)
                plt.ylabel("User ->", fontproperties=font_prop)
                st.pyplot(f)

            with col2: 
                st.dataframe(percent_messages_df)

        #_________________________________ Wordcloud ____________________________________#
        st.title("WORD AND EMOJI ANALYSIS")
        
        f, ax = plt.subplots(figsize=(10, 10))
        df = create_wordcloud(selected_user, chat_df)
        # Add the unimportant/irrelevant words in the STOPWORDS
        STOPWORDS.add("Media")
        STOPWORDS.add("omitted")
        STOPWORDS.add("Birthday Happy")
        STOPWORDS.add("Happy Birthday")

        st.header('Word Cloud')
        wc = WordCloud(stopwords=STOPWORDS, background_color='white', width=800, height=400).generate(' '.join(df['message'].astype(str)))
        plt.imshow(wc, interpolation='bilinear')
        plt.axis('off')
        st.pyplot(f)


        #----------------------------- Most common words -----------------------------#    
        
        topwords_df = most_used_words(selected_user, chat_df)

        st.header("Most common words")
        f, ax = plt.subplots(figsize=(6, 6))

        sns.barplot(x=topwords_df.values.flatten(), y=topwords_df.index).set_title("Most Common Words", fontdict={'size':20, 'weight':'bold'})
        plt.rc('axes', labelsize=30)    
        plt.xlabel("Word Frequency", fontproperties=font_prop)
        plt.ylabel("Word ", fontproperties=font_prop)
        st.pyplot(f)  

        
        # _________________________________ TOP EMOJIS ANALYSIS ____________________________#
        
        emoji_df = top_emojis_used(selected_user, chat_df)
        st.header("Emoji Analysis")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader('Emoji Dataframe')
            st.dataframe(emoji_df)

        with col2:
            st.subheader('Emoji Pie chart')
            font_path = font_manager.findfont(font_manager.FontProperties(family=['Noto Color Emoji']))
            plt.rcParams['font.family'] = font_manager.FontProperties(fname=font_path).get_name()
            f, ax = plt.subplots()
            palette_color = sns.color_palette('bright')
            ax.pie(emoji_df.head(N_EMOJIS_TO_DISPLAY)['count'].values, labels=emoji_df.head(N_EMOJIS_TO_DISPLAY)['emoji'].values, autopct="%0.2f")
            st.pyplot(f)



else:
    st.sidebar.write("Please upload a file.")





