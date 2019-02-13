import requests
import sys
import json
from bs4 import BeautifulSoup


input_tweet = sys.argv[1]

def download_video(tweet_id: str):
    # get js file embedded in video html to get bearer token needed to hit the config endpoint for the tweet
    video_url = 'https://twitter.com/i/videos/tweet/' + tweet_id
    video_html = requests.get(video_url).text
    video_soup = BeautifulSoup(video_html, 'html.parser')

    url_js_file = video_soup.find('script')['src']
    js_file = requests.get(url_js_file).text

    """
    TODO: Clean this mess by using regex instead  
    """
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
    config_url = 'https://api.twitter.com/1.1/videos/tweet/config/' + tweet_id + '.json'
    config_response = requests.get(config_url, headers={'Authorization': token}).text
    root_m3u8_url = json.loads(config_response)['track']['playbackUrl']
    m3u8 = requests.get(root_m3u8_url, headers={'Authorization': token}).text

    # pick out the last row (highest res file) of the m3u8 file
    highest_res_url = 'https://video.twimg.com' + m3u8.splitlines()[-1]
    video_as_m3u8 = requests.get(highest_res_url).text
    for line in video_as_m3u8.splitlines():
         print(line)

    """
    TODO: Download each of the chunks, concatenate them, and persist them locally
    """

download_video(input_tweet)