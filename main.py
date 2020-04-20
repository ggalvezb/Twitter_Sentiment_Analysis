from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from googletrans import Translator
import tweepy
import numpy as np
import re
import seaborn as sns
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import csv
import time
import pandas as pd
import nltk

translator = Translator()

#Conector twitter
consumer_key="XcVcYzGhwhtwlMik8RyKC8clg"
consumer_secret="PYQLPqPdwMGdupuoM6DwrwYaDkfAZ1CrETvPQp6BBlGwEuRgOB"
access_token="894532895548862468-FjtiXlybXh9Y551PMAMdHMmHE5sN0YL"
access_token_secret="fRTPkf0HCc1mNNglNZPLGx1CzZn0oDAptAt3FIGfHNtEb"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)


def sentiment_analyzer_scores(text, engl=True):
    if engl:
        trans = text
    else:
        trans = translator.translate(text).text
    score = analyser.polarity_scores(trans)
    lb = score['compound']
    if lb >= 0.05:
        return 1
    elif (lb > -0.05) and (lb < 0.05):
        return 0
    else:
        return -1

def list_tweets(user_id, count, prt=False):
    tweets = api.user_timeline(
        "@" + user_id, count=count, tweet_mode='extended')
    tw = []
    for t in tweets:
        tw.append(t.full_text)
        if prt:
            print(t.full_text)
            print()
    return tw

def remove_pattern(input_txt, pattern):
    r = re.findall(pattern, input_txt)
    for i in r:
        input_txt = re.sub(i, '', input_txt)        
    return (input_txt)

def clean_tweets(lst):
    # remove twitter Return handles (RT @xxx:)
    lst = np.vectorize(remove_pattern)(lst, "RT @[\w]*:")
    # remove twitter handles (@xxx)
    lst = np.vectorize(remove_pattern)(lst, "@[\w]*")
    # remove URL links (httpxxx)
    lst = np.vectorize(remove_pattern)(lst, "https?://[A-Za-z0-9./]*")
    # remove special characters, numbers, punctuations (except for #)
    lst = np.core.defchararray.replace(lst, "[^a-zA-Z#]", " ")
    return (lst)

def anl_tweets(lst, title='Tweets Sentiment', engl=True ):
    sents = []
    for tw in lst:
        try:
            st = sentiment_analyzer_scores(tw, engl)
            sents.append(st)
        except:
            sents.append(0)
    ax = sns.distplot(
        sents,
        kde=False,
        bins=3)
    ax.set(xlabel='Negative                Neutral                 Positive',
           ylabel='#Tweets',
          title="Tweets of @"+title)
    return sents

def word_cloud(wd_list):
    stopwords = set(STOPWORDS)
    all_words = ' '.join([text for text in wd_list])
    wordcloud = WordCloud(
        background_color='white',
        stopwords=stopwords,
        width=1600,
        height=800,
        random_state=21,
        colormap='jet',
        max_words=50,
        max_font_size=200).generate(all_words)

    plt.figure(figsize=(12, 10))
    plt.axis('off')
    plt.imshow(wordcloud, interpolation="bilinear")

##### track #####
def twitter_stream_listener(file_name, filter_track, follow=None, locations=None, languages=None, time_limit=20):
    class CustomStreamListener(tweepy.StreamListener):
        def __init__(self, time_limit):
            self.start_time = time.time()
            self.limit = time_limit
            # self.saveFile = open('abcd.json', 'a')
            super(CustomStreamListener, self).__init__()

        def on_status(self, status):
            if (time.time() - self.start_time) < self.limit:
                print(".", end="")
                # Writing status data
                with open(file_name, 'a',encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        status.author.screen_name, status.created_at,
                        status.text
                    ])
            else:
                print("\n\n[INFO] Closing file and ending streaming")
                return False

        def on_error(self, status_code):
            if status_code == 420:
                print('Encountered error code 420. Disconnecting the stream')
                # returning False in on_data disconnects the stream
                return False
            else:
                print('Encountered error with status code: {}'.format(
                    status_code))
                return True  # Don't kill the stream

        def on_timeout(self):
            print('Timeout...')
            return True  # Don't kill the stream

    # Writing csv titles
    print('\n[INFO] Open file: [{}] and starting {} seconds of streaming for {}\n'.format(file_name, time_limit, filter_track))
    with open(file_name, 'w',encoding="latin-1") as f:
        writer = csv.writer(f)
        writer.writerow(['author', 'date', 'text'])

    streamingAPI = tweepy.streaming.Stream(
        auth, CustomStreamListener(time_limit=time_limit))
    streamingAPI.filter(
        track=filter_track,
        follow=follow,
        locations=locations,
        languages=languages,
    )
    f.close()

def hashtag_extract(x):
    hashtags = []
    # Loop over the words in the tweet
    for i in x:
        ht = re.findall(r"#(\w+)", i)
        hashtags.append(ht)
    return hashtags


##### Buscador de usuario especifico #####
user_id = 'joseantoniokast'
count=500
tw_user = clean_tweets(list_tweets(user_id, count))
tw_user_sent = anl_tweets(tw_user, user_id)
word_cloud(tw_user)


#Buscador de palabras especificas
filter_track = ['violencia']
file_name = 'Degenerado.csv'
twitter_stream_listener (file_name, filter_track, time_limit=30)

df_tws = pd.read_csv(file_name,encoding='utf-8')
df_tws['text'] =  clean_tweets(df_tws['text'])
df_tws['sent'] = anl_tweets(df_tws.text)
word_cloud(df_tws.text)

# Palabras de tweets positivos
tws_pos = df_tws['text'][df_tws['sent'] == 1]
word_cloud(tws_pos)

# Palabras de tweets negativos
tws_pos = df_tws['text'][df_tws['sent'] == -1]
word_cloud(tws_pos)


# Extraccion de hashtag en tweets positivos
HT_positive = hashtag_extract(df_tws['text'][df_tws['sent'] == 1])

# Extraccion de hashtag en tweets negativos
HT_negative = hashtag_extract(df_tws['text'][df_tws['sent'] == -1])

# unnesting list
HT_positive = sum(HT_positive,[])
HT_negative = sum(HT_negative,[])

# Tweets positivos
a = nltk.FreqDist(HT_positive)
d = pd.DataFrame({'Hashtag': list(a.keys()),
                  'Count': list(a.values())})
# Seleccion de los 10 hashtag mas usados  
d = d.nlargest(columns="Count", n = 10) 
plt.figure(figsize=(16,5))
ax = sns.barplot(data=d, x= "Hashtag", y = "Count")
ax.set(ylabel = 'Count')
plt.show()


# Tweets negativos
b = nltk.FreqDist(HT_negative)
e = pd.DataFrame({'Hashtag': list(b.keys()), 'Count': list(b.values())})
# Seleccion de los 10 hashtag mas usados  
e = e.nlargest(columns="Count", n = 10)   
plt.figure(figsize=(16,5))
ax = sns.barplot(data=e, x= "Hashtag", y = "Count")
ax.set(ylabel = 'Count')
plt.show()