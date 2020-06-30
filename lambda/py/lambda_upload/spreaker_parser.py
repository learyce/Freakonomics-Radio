import logging
import feedparser
import requests
import atoma

from alexa import data, util

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

test = requests.get("https://www.spreaker.com/show/2885244/episodes/feed")
NewsFeed3 = atoma.parse_rss_bytes(test.content)

test2 = requests.get("https://www.omnycontent.com/d/playlist/aaea4e69-af51-495e-afc9-a9760146922b/14a43378-edb2-49be-8511-ab0d000a7030/d1b9612f-bb1b-4b85-9c0c-ab0d004ab37a/podcast.rss")
NewsFeed4 = atoma.parse_rss_bytes(test2.content)

NewsFeed = feedparser.parse("https://www.omnycontent.com/d/playlist/aaea4e69-af51-495e-afc9-a9760146922b/14a43378-edb2-49be-8511-ab0d000a7030/d1b9612f-bb1b-4b85-9c0c-ab0d004ab37a/podcast.rss")
NewsFeed2 = feedparser.parse("https://www.spreaker.com/show/2885244/episodes/feed")

entry = NewsFeed.entries[1]
