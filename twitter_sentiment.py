import tweepy
from transformers import pipeline
from utils import load_config
import os

def fetch_tweets():
    config = load_config()
    twitter_cfg = config["twitter"]
    bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
    client = tweepy.Client(bearer_token=bearer_token)
    tweets = []
    for tweet in tweepy.Paginator(
            client.search_recent_tweets,
            query=twitter_cfg["query"],
            tweet_fields=["text"],
            max_results=100).flatten(limit=twitter_cfg["max_tweets"]):
        tweets.append(tweet.text)
    return tweets

def analyze_sentiment(tweets):
    sentiment_analyzer = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment-latest")
    scores = []
    for tweet in tweets[:32]:  # batch size limit
        out = sentiment_analyzer(tweet)[0]
        scores.append(1 if out['label'] == 'Positive' else -1 if out['label'] == 'Negative' else 0)
    return sum(scores)/len(scores) if scores else 0

def get_twitter_sentiment():
    try:
        tweets = fetch_tweets()
        score = analyze_sentiment(tweets)
        return score
    except Exception as e:
        return 0  # Fallback: neutral if Twitter API/model fails
