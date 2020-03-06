import tweepy
import json

consumer_key="XcVcYzGhwhtwlMik8RyKC8clg"
consumer_secret="PYQLPqPdwMGdupuoM6DwrwYaDkfAZ1CrETvPQp6BBlGwEuRgOB"
access_token="894532895548862468-FjtiXlybXh9Y551PMAMdHMmHE5sN0YL"
access_token_secret="fRTPkf0HCc1mNNglNZPLGx1CzZn0oDAptAt3FIGfHNtEb"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

# con este objeto realizaremos todas las llamadas al API
api = tweepy.API(auth,
                 wait_on_rate_limit=True,
                 wait_on_rate_limit_notify=True)


