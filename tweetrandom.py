#!/usr/bin/env python3

import csv, random, yaml, requests, os
from io import BytesIO
import atproto
from mastodon import Mastodon
from PIL import Image

fullpath = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(fullpath, "config.yaml")) as f:
    config = yaml.safe_load(f)

with open(os.path.join(fullpath, "tweetswithimgs.csv")) as f:
    tweetreader = csv.reader(f)
    tweetlist = list(tweetreader)

mastodon_client_id = config['mastodon_client_id']
mastodon_client_secret = config['mastodon_client_secret']
mastodon_token = config['mastodon_token']

mastodon = Mastodon(client_id = mastodon_client_id, client_secret = mastodon_client_secret, access_token = mastodon_token, api_base_url = 'https://botsin.space')

bsky_client = atproto.Client()
bsky_client.login(config['bluesky_username'], config['bluesky_password'])

atweet = random.choice(tweetlist)

useragent = config['user_agent']

res = requests.get(atweet[1], headers={'User-Agent':useragent})
photo = Image.open(BytesIO(res.content))

wc_width, wc_height = photo.size
long_edge = int(1.1 * max(wc_width,wc_height))

paste_x = int(long_edge/2 - wc_width/2)
paste_y = int(long_edge/2 - wc_height/2)

bg = Image.new('RGB',(long_edge,long_edge),(255, 252, 233))
bg.paste(photo,(paste_x, paste_y))

image_io = BytesIO()

bg.save(image_io,format='jpeg')

# Mastodon upload, toot

image_io.seek(0)

mast_media = mastodon.media_post(image_io, mime_type='image/jpeg')
mastodon.status_post(status=atweet[0], media_ids=[mast_media['id']])

# Bluesky skeet

image_io.seek(0)

bsky_client.send_image(text=atweet[0], image=image_io, image_alt=atweet[0])
