import redeye.popsources as popsources
import config
import pymongo
import random
from pprint import pprint
from datetime import datetime

mongo = config.mongo

con = pymongo.MongoClient(mongo['host'], mongo['port'])
db = con[mongo['database']]

pop_collection = db.pop_sources

evergreen_sources = (
    popsources.IMDBMovies,
    popsources.SongYearSongs
)

for source in evergreen_sources:
    for year in range(1980, 2013):
        fetcher = source(year)
        for (title, attribution, tags) in fetcher.fetch():
            n_matches = [w[0] for w in tags.get('n', [])]
            v_matches = [w[0] for w in tags.get('v', [])]

            doc = {
                "_id": title.lower(),
                "title": title,
                "attribution": attribution,
                "created": datetime.now(),
                "source": fetcher.source,
                "type": fetcher.item_type,
                "n_chars": n_matches or None,
                "v_matches": v_matches or None,
                "n_tags": tags.get('n'),
                "v_tags": tags.get('v'),
                "year": year,
                "rand": random.random()
            }

            pprint(doc)

            pop_collection.save(doc)
