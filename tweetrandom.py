#!/usr/bin/env python3

import csv, random, yaml, requests
from io import BytesIO
from twython import Twython
from PIL import Image

config = yaml.load(open("/home/pom/config.yaml"))

tweetfile = open("/home/pom/tweetswithimgs.csv")
tweetreader = csv.reader(tweetfile)
tweetlist = list(tweetreader)

twitter_app_key = config['twitter_app_key']
twitter_app_secret = config['twitter_app_secret']
twitter_oauth_token = config['twitter_oauth_token']
twitter_oauth_token_secret = config['twitter_oauth_token_secret']

twitter = Twython(twitter_app_key, twitter_app_secret, twitter_oauth_token, twitter_oauth_token_secret)

atweet = random.choice(tweetlist)

res = requests.get(atweet[1])
photo = Image.open(BytesIO(res.content))

wc_width, wc_height = photo.size
long_edge = int(1.1 * max(wc_width,wc_height))

paste_x = int(long_edge/2 - wc_width/2)
paste_y = int(long_edge/2 - wc_height/2)

bg = Image.new('RGB',(long_edge,long_edge),(255, 252, 233))
bg.paste(photo,(paste_x, paste_y))

image_io = BytesIO()

bg.save(image_io,format='jpeg')

image_io.seek(0)

response = twitter.upload_media(media=image_io)
twitter.update_status(status=atweet[0], media_ids=[response['media_id']])
