import feedparser
import re
from datetime import datetime
from tornado.httpclient import AsyncHTTPClient

basic_chars = re.compile("[A-Za-z ]+")
strip_parens = re.compile("\(.*?\)")

class NYTimesSource(object):

    def fetch(self, callback):

        def _fetch_results(response):
            items = []
            if not response.error:
                entries = feedparser.parse(response.body).entries
                for entry in entries:
                    try:
                        terms = [strip_parens.sub('', t['term']).strip() for t in entry['tags']]
                    except KeyError:
                        callback(items)
                        return

                    categories = [c for c in terms if len(basic_chars.findall(c)) == 1 and c.count(" ") < 2 and len(c) > 4]
                    if len(categories) > 0:
                        items.append((entry['title'], categories, entry['link']))
            callback(items)

        http_client = AsyncHTTPClient()
        http_client.fetch(self.feed_url, _fetch_results)

class WorldNews(NYTimesSource):

    news_type = "World"

    def __init__(self):
        self.feed_url = "http://rss.nytimes.com/services/xml/rss/nyt/World.xml"
        self.web_url = "http://www.nytimes.com/pages/world/index.html"

class USNews(NYTimesSource):

    news_type = "US"

    def __init__(self):
        self.feed_url = "http://rss.nytimes.com/services/xml/rss/nyt/US.xml"
        self.web_url = "http://www.nytimes.com/pages/national/index.html"

class PoliticsNews(NYTimesSource):

    news_type = "Politics"

    def __init__(self):
        self.feed_url = "http://rss.nytimes.com/services/xml/rss/nyt/Politics.xml"
        self.web_url = "http://www.nytimes.com/pages/politics/index.html"

class ScienceNews(NYTimesSource):

    news_type = "Science"

    def __init__(self):
        self.feed_url = "http://rss.nytimes.com/services/xml/rss/nyt/Science.xml"
        self.web_url = "http://www.nytimes.com/pages/science/index.html"

class SportsNews(NYTimesSource):

    news_type = "Sports"

    def __init__(self):
        self.feed_url = "http://rss.nytimes.com/services/xml/rss/nyt/Sports.xml"
        self.web_url = "http://www.nytimes.com/pages/sports/index.html"


sources = {
    "world": WorldNews,
    "national": USNews,
    "politics": PoliticsNews,
    "science": ScienceNews,
    "sports": SportsNews
}

lookup_times = dict()

def fetch_news(news_type, callback):

    def _response(results):
        lookup_times[news_type] = {
            "time": datetime.now(),
            "results": results
        }
        callback(results)

    if news_type in lookup_times and (lookup_times[news_type]['time'] - datetime.now()).seconds < 120:
        callback(lookup_times[news_type]['results'])
    else:
        source = sources[news_type]()
        source.fetch(_response)
