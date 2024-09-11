import emoji.unicode_codes
from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
import emoji

extract = URLExtract()


def fetch_stats(sel_user,df):

    if sel_user != 'All Chats':  # for particular user
        df = df[df['user']==sel_user]
    # 1. fetch no of messages
    num_messages = df.shape[0]
    # 2. no of words
    words=[]
    for i in df['message']:
        words.extend(i.split())

    # 3. no of media messages
    num_media_msg = df[df['message']=='<Media omitted>\n'].shape[0]

    # 4. no of links shared
    links=[]
    for i in df['message']:
        links.extend(extract.find_urls(i))

    return num_messages , len(words) , num_media_msg, len(links)

def most_busy_user(df):
    # for most busy user
    x=df['user'].value_counts().head()
    # for finding percentage of user contribution in chat
    df= round((df['user'].value_counts()/df.shape[0])*100,2).reset_index().rename(columns={'index':'name','user':'percent'})

    return x, df


def create_wordcloud(sel_user, df):
    f=open("C:\\Users\\velpr\\OneDrive\\Documents\\ml projects\\whatsapp chat analyser\\stop_hinglish.txt",'r')
    stop_words = f.read()


    if sel_user != 'All Chats':  # for particular user
        df = df[df['user']==sel_user]
    
    # to remove group notification and media omitted msg
    temp =df[df['user']!='Group_notification']
    temp=temp[temp['message']!='<Media omitted>\n']

    def remove_stopwords(message):
        y=[]
        for word in message.lower().split():
            if word not in stop_words:
                y.append(word)
        return " ".join(y)
    

    wc = WordCloud(width=500, height=500,min_font_size=10,background_color='grey')
    temp['message']= temp['message'].apply(remove_stopwords)
    df_wc  = wc.generate(temp['message'].str.cat(sep=" "))
    return df_wc

def most_common_words(sel_user,df):
    f=open("C:\\Users\\velpr\\OneDrive\\Documents\\ml projects\\whatsapp chat analyser\\stop_hinglish.txt",'r')
    stop_words = f.read()

    if sel_user != 'All Chats':  # for particular user
        df = df[df['user']==sel_user]
# to remove group notification and media omitted msg
    temp =df[df['user']!='Group_notification']
    temp=temp[temp['message']!='<Media omitted>\n']

    words=[]
    #to remove stopwords
    for message in temp['message']:
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)
    
    common_words_df  = pd.DataFrame(Counter(words).most_common(20))
    return common_words_df

def emoji_analyser(sel_user,df):
    if sel_user != 'All Chats':  # for particular user
        df = df[df['user']==sel_user]

    emojis=[]
    for message in df['message']:
        emojis.extend([c for c in message if emoji.is_emoji(c)])
    
    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))
    return emoji_df

def monthly_timeline(sel_user, df):
    if sel_user != 'All Chats':  # for particular user
        df = df[df['user']==sel_user]
    
    timeline = df.groupby(['year','month_num','month']).count()['message'].reset_index()

    time=[]
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + '-' + str(timeline['year'][i]))

    timeline['time']= time

    return timeline

def daily_timeline(sel_user,df):
    if sel_user != 'All Chats':  # for particular user
        df = df[df['user']==sel_user]

    daily_timeline = df.groupby('only_date').count()['message'].reset_index()

    return daily_timeline

def week_activity(sel_user,df):
    if sel_user != 'All Chats':  # for particular user
        df = df[df['user']==sel_user]
   
    return df['day_name'].value_counts()

def month_activity(sel_user,df):
    if sel_user != 'All Chats':  # for particular user
        df = df[df['user']==sel_user]

    return df['month'].value_counts()

def activity_heatmap(sel_user,df):
    if sel_user != 'All Chats':  # for particular user
        df = df[df['user']==sel_user]

    act_heatmap =df.pivot_table(index='day_name',columns='period',values='message',aggfunc='count').fillna(0)
    return act_heatmap



