#!/usr/bin/env python3

import csv, random, yaml, requests, os
from io import BytesIO
from mastodon import Mastodon
from twython import Twython
from PIL import Image

from datetime import datetime, timezone

fullpath = os.path.dirname(os.path.realpath(__file__))
BLUESKY_BASE_URL = "https://bsky.social/xrpc"

with open(os.path.join(fullpath, "config.yaml")) as f:
    config = yaml.safe_load(f)

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

def authenticate_bluesky():
    resp = requests.post(
        BLUESKY_BASE_URL + "/com.atproto.server.createSession",
        json={"identifier": config['bluesky_username'], "password": config['bluesky_password']},
    )
    resp_data = resp.json()
    jwt = resp_data["accessJwt"]
    did = resp_data["did"]
    return jwt, did

(bsky_jwt, bsky_did) = authenticate_bluesky()

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

# Twitter upload, tweet

image_io.seek(0)

response = twitter.upload_media(media=image_io)
twitter.update_status(status=atweet[0], media_ids=[response['media_id']])

# Mastodon upload, toot

image_io.seek(0)

mast_media = mastodon.media_post(image_io, mime_type='image/jpeg')
mastodon.status_post(status=atweet[0], media_ids=[mast_media['id']])

# Bluesky upload, skeet

image_io.seek(0)

headers = {"Authorization": "Bearer " + bsky_jwt}

bsky_media_resp = requests.post(
        BLUESKY_BASE_URL + "/com.atproto.repo.uploadBlob",
        data=image_io,
        headers={**headers, "Content-Type": "image/jpg"})

img_blob = bsky_media_resp.json().get("blob")

iso_timestamp = datetime.now(timezone.utc).isoformat()
iso_timestamp = (
    iso_timestamp[:-6] + 'Z'
)

post_data = {
    "repo": bsky_did,
    "collection": "app.bsky.feed.post",
    "record": {
        "$type": "app.bsky.feed.post",
        "text": atweet[0],
        "createdAt": iso_timestamp,
        "embed": {"$type": "app.bsky.embed.images", "images":
            [{"image": img_blob,
              "alt":atweet[0]}]},
    }
}

resp = requests.post(BLUESKY_BASE_URL + "/com.atproto.repo.createRecord",
                        json=post_data,
                        headers=headers)
