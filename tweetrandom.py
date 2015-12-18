#!/usr/bin/env python3

import random, yaml, requests, json, random
from io import BytesIO
from twython import Twython

TOTAL_FRUIT = 7574
CONFIG = "config.yaml"
TWEETS_FILE = "tweetswithimgs.json"
NEXT_LIST_FILE = "nexttweetlist.json"

def get_config():
    with open(CONFIG, 'r') as c:
        config = yaml.load(c)
    return config

def get_tweetlist():
    with open(TWEETS_FILE, 'r') as tweetfile:
        tweetlist = json.loaf(tweetfile)
    return tweetlist

def get_next_tweet_list():
    with open(NEXT_LIST_FILE, 'r') as f:
        next_tweet_list = json.load(f)
    return next_tweet_list

def write_next_tweet_list(next_tweet_list):
    with open(NEXT_LIST_FILE, 'w') as f:
        json.dump(next_tweet_list, f)

def get_twitter_instance(config):
    twitter_app_key = config['twitter_app_key']
    twitter_app_secret = config['twitter_app_secret']
    twitter_oauth_token = config['twitter_oauth_token']
    twitter_oauth_token_secret = config['twitter_oauth_token_secret']
    return Twython(twitter_app_key, twitter_app_secret, twitter_oauth_token, twitter_oauth_token_secret)

def get_fruit_image(tweet_data):
    res = requests.get(tweet_data[1])
    photo = BytesIO(res.content)

def main():
    config = get_config()
    tweetlist = get_tweetlist()
    twitter = get_twitter_instance(config)

    next_tweet_list = get_next_tweet_list()
    if len(next_tweet_list) == 0:
        next_tweet_list = random.shuffle(range(TOTAL_FRUIT))
    tweet_data = tweetlist[str(next_tweet_list.pop(0))]
    write_next_tweet_list(next_tweet_list)

    photo = get_fruit_image(next_tweet)

    response = twitter.upload_media(media=photo)
    twitter.update_status(status=tweet_data[0], media_ids=[response['media_id']])


if __name__ == "__main__":
    main()
