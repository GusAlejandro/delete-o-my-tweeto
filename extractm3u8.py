"""
This module handles downloading twitter videos using the tweet id
"""
import sys
import json
import uuid
import requests
import os
from bs4 import BeautifulSoup


INPUT_TWEET = sys.argv[1]

# TODO: refactor this module to handle all twitter media downloads, not just video

def download_video(m3u8_text: str, tweet_id: str):
    """
    Handles storing all ts chunks in the m3u8 text
    :param m3u8_text: root m3u8 file as text, has urls for all video chunks
    :param tweet_id: reference id for tweet
    :return: None
    """
    video_chunks = ''
    ts_prefix = "https://video.twimg.com"
    for line in m3u8_text.splitlines():
        if "/ext_tw_video/" in line:
            r = requests.get(ts_prefix + line)
            chunk_name = str(uuid.uuid4())
            open(chunk_name + '.ts', 'wb').write(r.content)
            video_chunks += chunk_name +'.ts' + ' '
    file_name = tweet_id + '.ts'
    os.system('cat ' + video_chunks + '> ' + file_name)

    # delete chunks
    for chunk in video_chunks.split():
        os.system('rm ' + chunk)


def get_root_m3u8_url(tweet_id: str, token: str):
    config_url = 'https://api.twitter.com/1.1/videos/tweet/config/' + tweet_id + '.json'
    config_response = requests.get(config_url, headers={'Authorization': token})
    if config_response.status_code  == 429:
        return None
    else:
        return json.loads(config_response.text)['track']['playbackUrl']





def main(tweet_id: str):
    """
    Main func.
    :param tweet_id: reference id for tweet
    :return: None
    """
    # get js file embedded in video html to get bearer token needed to hit the config endpoint for the tweet
    video_url = 'https://twitter.com/i/videos/tweet/' + tweet_id
    video_html = requests.get(video_url).text
    video_soup = BeautifulSoup(video_html, 'html.parser')

    url_js_file = video_soup.find('script')['src']
    js_file = requests.get(url_js_file).text

    # TODO: Clean this mess by using regex instead

    # extracts bearer token needed to call config endpoint
    token = ""
    index = 0
    unparsed_token = js_file.split('authorization:"')[1]
    letter = unparsed_token[index]
    while letter != '"':
        token += letter
        index += 1
        letter = unparsed_token[index]

    # call the config endpoint to extract root m3u8 file
    root_m3u8_url = get_root_m3u8_url(tweet_id, token)

    if not root_m3u8_url:
        print("RATE LIMIT HIT")
        return

    root_m3u8 = requests.get(root_m3u8_url, headers={'Authorization': token}).text

    # pick out the last row (highest res file) of the m3u8 file
    highest_res_url = 'https://video.twimg.com' + root_m3u8.splitlines()[-1]
    video_chunks = requests.get(highest_res_url).text

    download_video(video_chunks, tweet_id)


main(INPUT_TWEET)
