"""
This module handles downloading videos and photos attached to tweets
"""
import json
import uuid
import os
import requests
from bs4 import BeautifulSoup


# INPUT_TWEET = sys.argv[1]

def download_video(m3u8_text: str, tweet_id: str):
    """
    Handles storing all ts chunks in the m3u8 text
    :param m3u8_text:
    :param tweet_id:
    :return: None
    """
    video_chunks = ''
    ts_prefix = "https://video.twimg.com"
    for line in m3u8_text.splitlines():
        if "/ext_tw_video/" in line:
            req = requests.get(ts_prefix + line)
            chunk_name = str(uuid.uuid4())
            open(chunk_name + '.ts', 'wb').write(req.content)
            video_chunks += chunk_name +'.ts' + ' '
    file_name = tweet_id + '.ts'
    os.system('cat ' + video_chunks + '> ' + file_name)

    # delete chunks
    for chunk in video_chunks.split():
        os.system('rm ' + chunk)


def get_root_m3u8_url(tweet_id: str, token: str):
    """
    GET request on the tweet config endpoint
    :param tweet_id:
    :param token:
    :return: root m3u8 url
    """
    config_url = 'https://api.twitter.com/1.1/videos/tweet/config/' + tweet_id + '.json'
    config_response = requests.get(config_url, headers={'Authorization': token})
    if config_response.status_code == 429:
        return None
    return json.loads(config_response.text)['track']['playbackUrl']


def video_main(tweet_id: str):
    """
    Main func for video.
    :param tweet_id:
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


def download_photo(image_url: str, tweet_id: str):
    """
    Downloads the image at the image_url specified in the parameters
    :param image_url:
    :param tweet_id:
    :return:
    """
    req = requests.get(image_url)
    file_name = str(uuid.uuid4())
    open(tweet_id + '/' + file_name + '.jpg', 'wb').write(req.content)


def photo_main(tweet_id: str, username: str):
    """
    Main func for photo.
    :param tweet_id:
    :param username:
    :return: None
    """
    os.mkdir(tweet_id)
    tweet_url = 'https://twitter.com/' + username + '/status/' + tweet_id
    tweet_html = requests.get(tweet_url).text

    # in order to handle tweet thread scenario, uses two layers of beautifulsoup
    tweet_soup = BeautifulSoup(tweet_html, 'html.parser')
    top_level_tag = str(tweet_soup.find_all("div", {'data-tweet-id': tweet_id}))

    # identifies images attached to tweet, not including avi's
    image_container_soup = BeautifulSoup(top_level_tag, 'html.parser')
    image_list = image_container_soup.find_all("img")
    for image in image_list:
        if 'data-aria-label-part' in str(image):
            download_photo(image['src'], tweet_id)



# video_main(INPUT_TWEET)
photo_main('1095158234128601089', 'GusAlejandro_')
