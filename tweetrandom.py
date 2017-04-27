#!/usr/bin/env python3

import csv, random, yaml, requests, os
from io import BytesIO
from mastodon import Mastodon
from twython import Twython
from PIL import Image

fullpath = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(fullpath, "config.yaml")) as f:
    config = yaml.load(f)

with open(os.path.join(fullpath, "tweetswithimgs.csv")) as f:
    tweetreader = csv.reader(f)
    tweetlist = list(tweetreader)

twitter_app_key = config['twitter_app_key']
twitter_app_secret = config['twitter_app_secret']
twitter_oauth_token = config['twitter_oauth_token']
twitter_oauth_token_secret = config['twitter_oauth_token_secret']

twitter = Twython(twitter_app_key, twitter_app_secret, twitter_oauth_token, twitter_oauth_token_secret)

mastodon_client_id = config['mastodon_client_id']
mastodon_client_secret = config['mastodon_client_secret']
mastodon_token = config['mastodon_token']

mastodon = Mastodon(client_id = mastodon_client_id, client_secret = mastodon_client_secret, access_token = mastodon_token, api_base_url = 'https://botsin.space')

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

# Twitter upload, tweet

image_io.seek(0)

response = twitter.upload_media(media=image_io)
twitter.update_status(status=atweet[0], media_ids=[response['media_id']])

# Mastodon upload, toot

image_io.seek(0)

mast_media = mastodon.media_post(image_io, mime_type='image/jpeg')
mastodon.status_post(status=atweet[0], media_ids=[mast_media['id']])
