import pandas
import sys
from extract_media import get_media

df = pandas.read_csv('tweets.csv')
# print(df['text'][460])


def process_csv(tweet_id: str):
    """
    Potential flow:
    sart with scraping tweet to discover if its video, photo, or just text
    3 paths, if image, call
    :return:
    """
    get_media(tweet_id)


process_csv(sys.argv[1])
