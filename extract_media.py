"""
This module handles downloading videos and photos attached to tweets
"""
import json
import uuid
import os
import requests
from bs4 import BeautifulSoup


def download_video_from_m3u8(m3u8_text: str, tweet_id: str):
    """
    Handles storing all ts chunks in the m3u8 text
    :param m3u8_text:
    :param tweet_id:
    :return: None
    """
    video_chunks = ''
    ts_prefix = "https://video.twimg.com"
    for line in m3u8_text.splitlines():
        if "/ext_tw_video/" in line or "/amplify_video/" in line:
            req = requests.get(ts_prefix + line)
            chunk_name = str(uuid.uuid4())
            open(chunk_name + '.ts', 'wb').write(req.content)
            video_chunks += chunk_name +'.ts' + ' '
    file_name = tweet_id + '.ts'
    os.system('cat ' + video_chunks + '> ' + file_name)

    # delete chunks
    for chunk in video_chunks.split():
        os.system('rm ' + chunk)
    print("Video downloaded successfully")


def download_video_from_mp4(mp4_url: str, tweet_id: str):
    """
    Short func to download vid from mp4 url
    :param mp4_url:
    :param tweet_id:
    :return:
    """
    req = requests.get(mp4_url)
    open(tweet_id + '.mp4', 'wb').write(req.content)
    print("Video downloaded successfully")


def get_resource_url(tweet_id: str, token: str):
    """
    GET request on the tweet config endpoint
    :param tweet_id:
    :param token:
    :return: Resource URL which is either direct mp4 or root m3u8 file
    """
    config_url = 'https://api.twitter.com/1.1/videos/tweet/config/' + tweet_id + '.json'
    config_response = requests.get(config_url, headers={'Authorization': token})
    if config_response.status_code == 429:
        return None
    return json.loads(config_response.text)['track']['playbackUrl']


def video_main(tweet_id: str):
    """
    Main func for video, handles both m3u8 and mp4 resource urls
    :param tweet_id:
    :return: None
    """
    # get js file embedded in video html to get bearer token needed to hit the config endpoint for the tweet
    video_url = 'https://twitter.com/i/videos/tweet/' + tweet_id
    video_html = requests.get(video_url).text
    video_soup = BeautifulSoup(video_html, 'html.parser')

    url_js_file = video_soup.find('script')['src']
    js_file = requests.get(url_js_file).text

    # extracts bearer token needed to call config endpoint, stores in var token
    # TODO: Clean this mess by using regex instead
    token = ""
    index = 0
    unparsed_token = js_file.split('authorization:"')[1]
    letter = unparsed_token[index]
    while letter != '"':
        token += letter
        index += 1
        letter = unparsed_token[index]

    # call the config endpoint using the bearer token to extract the mp4/m3u8 url from response
    resource_url = get_resource_url(tweet_id, token)

    if not resource_url:
        print("RATE LIMIT HIT")
        return

    if '.m3u8' in resource_url:
        # we have an m3u8 file
        root_m3u8 = requests.get(resource_url, headers={'Authorization': token}).text
        # pick out the last row (highest res file) of the m3u8 file
        highest_res_url = 'https://video.twimg.com' + root_m3u8.splitlines()[-1]
        m3u8 = requests.get(highest_res_url).text
        download_video_from_m3u8(m3u8, tweet_id)
    else:
        # we have an mp4 file
        download_video_from_mp4(resource_url, tweet_id)


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


def photo_main(tweet_id: str, images: list):
    """
    Main func for photo. Since tweets can contain multiple photos, it creates a directory to house them.
    :param tweet_id:
    :param images:
    :return: None
    """
    os.mkdir(tweet_id)
    for image_url in images:
        download_photo(image_url, tweet_id)


def get_media(tweet_id: str):
    """
    Entry point for csv_reader.py
    :param tweet_id:
    :return:
    """
    # we first need to scrape in order to determine if we have any media on the tweet
    tweet_url = 'https://twitter.com/' + 'username' + '/status/' + tweet_id
    tweet_html = requests.get(tweet_url).text
    tweet_soup = BeautifulSoup(tweet_html, 'html.parser')
    top_level_tag = str(tweet_soup.find_all("div", {'data-tweet-id': tweet_id}))

    media_soup = BeautifulSoup(top_level_tag, 'html.parser')
    video_tag = media_soup.find_all('div', {'class': 'PlayableMedia PlayableMedia--video'})

    image_tags = media_soup.find_all('img')
    # need to filter the collection of image tags, remove profile pictures
    image_list = []
    for image in image_tags:
        if 'data-aria-label-part' in str(image):
            image_list.append(image['src'])

    if video_tag:
        print("we have video")
        video_main(tweet_id)
    elif image_list:
        print("we have image(s)")
        photo_main(tweet_id, image_list)
    else:
        print("no media")
