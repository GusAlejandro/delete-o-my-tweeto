# delete-o-my-tweeto
Script that uses the twitter archive excel sheet template to delete any given tweets along with downloading any images/video attached to the tweets.

### State of the Project
This was a little project to cleanse my cringey, teenage tweets from my profile. This project lacks tests, exception catching, and has several areas for improvement (performance, etc.).

### Installation Guide
Clone this repo, pip install the requirements, create a config.json file with the following format:

```
{
  "CONSUMER_KEY": "xxx",
  "CONSUMER_SECRET": "xxx",
  "ACCESS_TOKEN": "xxx",
  "ACCESS_TOKEN_SECRET": "xxx"
}
```

These tokens/keys are provided by the Twitter Developer site. You will need them to access the delete tweet endpoint.

### Running The Script
```
python delete_my_tweets.py file_name.csv
```
The videos that are downloaded will be stored with the tweet_id as their name. The images will be stored in a directory named after the tweet id, but the image(s) within are randomly named w/uuid.
