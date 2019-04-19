"""
This module controls logic surrounding reading in the tweet archive, deleting & storing media of the tweets.
"""
import pandas
from tweet_deletion import initialize_and_return_api_object, delete_tweet
from extract_media import get_media

# TODO: Later add logic to validate file format


def process_csv(file_name: str):
    """
    Potential flow:
    sart with scraping tweet to discover if its video, photo, or just text
    3 paths, if image, call
    :return:
    """
    df = pandas.read_csv(file_name)
    api = initialize_and_return_api_object()
    for tweet in df.iterrows():
        tweet_id = str(tweet[1][0])
        print("Tweet ID:" + str(tweet_id))
        response = get_media(tweet_id)
        if response == "RATE LIMIT HIT":
            # TODO: Need to handle hitting the rate limit for downloading videos
            pass
        elif response == 'Tweet already deleted':
            print('Tweet already deleted')
        else:
            # happy path
            delete_tweet(tweet_id, api)
            print("Tweet was deleted")







process_csv('trial.csv')
