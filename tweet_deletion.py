"""
This module will handle any logic/requests that deal with deleting tweets
"""
import json
import tweepy


def initialize_and_return_api_object():
    """
    Uses config.json to create the tweepy api object
    :return: tweepy api object
    """
    file = open('config.json')
    data = json.load(file)
    auth = tweepy.OAuthHandler(data['CONSUMER_KEY'], data["CONSUMER_SECRET"])
    auth.set_access_token(data['ACCESS_TOKEN'], data['ACCESS_TOKEN_SECRET'])
    return tweepy.API(auth)


def delete_tweet(tweet_id: str, api: tweepy.API):
    """
    Deletes given tweet id.
    :param tweet_id:
    :param api:
    :return:
    """
    api.destroy_status(tweet_id)
