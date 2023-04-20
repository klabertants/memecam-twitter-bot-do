import tweepy
import requests
import urllib.parse
from PIL import Image
from io import BytesIO
import uuid

from caption_generator import generate_image_with_caption

from tinydb import TinyDB

db = TinyDB('db.json')

bearer_token = "AAAAAAAAAAAAAAAAAAAAAChTmwEAAAAAhyLo8jm4KI8JnvZYlAwYLLFUAAY%3DUai3HcradPDSXPZV36RyCFD0nN0zhu41mGeaMQnsmq97YitXaS"

client = tweepy.Client(
    consumer_key="H19yN1s3cJT2U2jaHgHOJuV6X",
    consumer_secret="Nxd07SkF3lVQIrfprbo1r1y6NdWdyYxp0O1t3dcDUaimWgzlrA",
    access_token="1646153796106559490-eOcZew0cQR77O1QMqKwNL430LiwEfW",
    access_token_secret="fzxTRKzzlp9L9GKjNbNNVWYrLEZnCA3AKHXL53Ro3kzGZ"
)

auth = tweepy.OAuthHandler("H19yN1s3cJT2U2jaHgHOJuV6X", "Nxd07SkF3lVQIrfprbo1r1y6NdWdyYxp0O1t3dcDUaimWgzlrA")
auth.set_access_token("1646153796106559490-eOcZew0cQR77O1QMqKwNL430LiwEfW",
                      "fzxTRKzzlp9L9GKjNbNNVWYrLEZnCA3AKHXL53Ro3kzGZ")
api = tweepy.API(auth)


def generate_image_with_caption_for_tweet(tweet_id, caption):
    input_path = "profile_pics/" + str(tweet_id) + ".jpg"
    result_path = "results/" + str(tweet_id) + "_" + str(uuid.uuid4()) + ".jpg"
    generate_image_with_caption(input_path, result_path, caption)
    return result_path


def get_tweet_info(id):
    url = "https://twitter154.p.rapidapi.com/tweet/details"

    headers = {
        "X-RapidAPI-Key": "71f17edc44msh2f73ac8d1f01d01p1ab07fjsnb6eb05cb7711",
        "X-RapidAPI-Host": "twitter154.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params={"tweet_id": id})
    return response.json()


def get_thread_starter_profile_picture(tweet):
    start_tweet_info = get_tweet_info(tweet.data['conversation_id'])

    fixed_url = start_tweet_info["user"]["profile_pic_url"].replace('_normal', '')

    return fixed_url


def get_img_url_from_tweet(id):
    tweet_info = get_tweet_info(id)

    if tweet_info["media_url"] is None:
        return None

    for media_url in tweet_info["media_url"]:
        return media_url

    return None


def gen_captions_for_picture(picture_url):
    meme_gen = requests.post(
        'https://api-m-7qtp55otdq-uw.a.run.app/generate_from_url?url=' + urllib.parse.quote(picture_url)
    )

    return meme_gen.json()


def create_and_upload_meme(tweet_id, img_url, caption):
    response = requests.get(img_url)

    img = Image.open(BytesIO(response.content))
    img.save("profile_pics/" + str(tweet_id) + ".jpg")

    result_path = generate_image_with_caption_for_tweet(tweet_id, caption)

    media = api.media_upload(result_path)

    return media.media_id


class MyStream(pytwitter.StreamApi):
    def on_tweet(self, tweet):
        print(tweet)


def run_main_loop():
    memecam_id = client.get_me().data.id

    since_id = 0
    items = db.all()
    if len(items) > 0:
        since_id = items[0]["tweet_id"]
    else:
        db.insert({"tweet_id": since_id})

    tweets = client.get_users_mentions(
        memecam_id,
        since_id=since_id,
        tweet_fields=["author_id", "attachments", "conversation_id", "in_reply_to_user_id", 'created_at'],
        user_auth=True
    )

    if tweets.data is None:
        print(since_id)
        return

    for tweet in tweets.data:
        thread_starter_profile_picture_url = get_thread_starter_profile_picture(tweet)
        captions = gen_captions_for_picture(thread_starter_profile_picture_url)
        if captions:
            caption = captions[0]['resulting_text']

            client.create_tweet(
                text="Nothing personal",
                in_reply_to_tweet_id=tweet.id,
                media_ids=[create_and_upload_meme(tweet.id, thread_starter_profile_picture_url, caption)]
            )
        else:
            print("No media")

    db.update({"tweet_id": tweets.data[-1].id})

