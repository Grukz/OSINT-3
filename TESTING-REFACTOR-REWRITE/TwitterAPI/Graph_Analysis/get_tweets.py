import tweetstream
from json import dumps
from collections import OrderedDict
from pymongo import MongoClient


def twitterStream():
    """Watch Twitter RealTime Stream for WatchList Elements"""
    words = ["hackers", "FBI"]
    with tweetstream.FilterStream("JollyJimBob", "delta0!23123", track=words,) as stream:
        for tweet in stream:
            if 'user' in tweet:
                created_at = tweet['created_at']
                mentions = tweet['entities']['user_mentions']
                id_string = tweet['user']['id_str']
                screen_name = tweet['user']['screen_name']
                tweet_text = tweet['text']
                try:
                    if len(mentions) > 0:
                        for record in mentions:
                            user_id = record['id_str']
                            user_name = record['screen_name']
                            user_mentions = "mentions"
                            keys = ['Date', 'ID', 'Name', 'Tweet', 'Mention', 'mUserId', 'mUserName']
                            values = [created_at, id_string, screen_name, tweet_text, user_mentions, user_id, user_name]
                            mentions_dict = dict(zip(keys, values))
                            ordered_mentions_dict = OrderedDict(sorted(mentions_dict.items(), key=lambda by_key: by_key[0]))
                            yield ordered_mentions_dict
                    else:
                        no_mentions = "no_mentions"
                        keys = ['Date', 'ID', 'Name', 'Tweet', 'Mention']
                        values = [created_at, id_string, screen_name, tweet_text, no_mentions]
                        no_mentions_dict = dict(zip(keys, values))
                        ordered_no_mentions_dict = OrderedDict(sorted(no_mentions_dict.items(), key=lambda by_key: by_key[0]))
                        yield ordered_no_mentions_dict
                except KeyError:
                    raise KeyError


def encode_json():
    """Encode Python dictionary object to JSON object"""
    for tweet_dict in twitterStream():
        if tweet_dict:
            yield dumps(tweet_dict)


def write_mongo(element):
    """Write JSON object to MongoDB"""
    connection = MongoClient('localhost', 27017)
    db = connection["twitter"]
    tweet_hits = db["tweets"]
    yield tweet_hits.insert(element)


def main():
    for tweet in encode_json():
        print tweet


if __name__ == '__main__':
    main()