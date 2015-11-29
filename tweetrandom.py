#!/usr/bin/env python3

import csv, random, yaml, requests
from io import BytesIO
from twython import Twython

config = yaml.load(open("config.yaml"))

tweetfile = open("tweetswithimgs.csv")
tweetreader = csv.reader(tweetfile)
tweetlist = list(tweetreader)

twitter_app_key = config['twitter_app_key']
twitter_app_secret = config['twitter_app_secret']
twitter_oauth_token = config['twitter_oauth_token']
twitter_oauth_token_secret = config['twitter_oauth_token_secret']

twitter = Twython(twitter_app_key, twitter_app_secret, twitter_oauth_token, twitter_oauth_token_secret)

atweet = random.choice(tweetlist)

res = requests.get(atweet[1])
photo = BytesIO(res.content)

response = twitter.upload_media(media=photo)
twitter.update_status(status=atweet[0], media_ids=[response['media_id']])
