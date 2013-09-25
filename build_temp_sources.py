import redeye.popsources as popsources
import config
import pymongo
import random
from pprint import pprint
from datetime import datetime, timedelta

mongo = config.mongo

con = pymongo.MongoClient(mongo['host'], mongo['port'])
db = con[mongo['database']]

pop_collection = db.pop_sources

temp_sources = (
    popsources.TVShows,
)

for pop_source in temp_sources:

    # First remove any very old records in this collection
    pop_collection.remove({
        "source": pop_source.source,
        "created": {
            '$lte': datetime.now() - timedelta(days=30)
        }
    })

    fetcher = pop_source()
    for (title, attribution, tags) in fetcher.fetch():
        n_matches = [w[0] for w in tags.get('n', [])]
        v_matches = [w[0] for w in tags.get('v', [])]

        doc = {
            "_id": title.lower(),
            "title": title,
            "attribution": attribution,
            "created": datetime.now(),
            "source": pop_source.source,
            "type": pop_source.item_type,
            "n_chars": n_matches or None,
            "v_matches": v_matches or None,
            "n_tags": tags.get('n'),
            "v_tags": tags.get('v'),
            "year": None,
            "rand": random.random()
        }

        pprint(doc)

        pop_collection.save(doc)
