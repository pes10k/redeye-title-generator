import redeye.newssources as newssources
import config
import pymongo
import random
import re

mongo = config.mongo

con = pymongo.MongoClient(mongo['host'], mongo['port'])
db = con[mongo['database']]

pop_collection = db.pop_sources


s = newssources.WorldNews()
entries = s.fetch()

for title, tags, link in entries:

    tag = random.choice(tags)
    first_char = tag[0].lower()

    doc = pop_collection.find_one({
        "n_chars": first_char,
        "rand": {
            "$gte": random.random(),
        }
    })

    if not doc:
        doc = pop_collection.find_one({
            "n_chars": first_char,
            "rand": {
                "$lte": random.random(),
            }
        })

    noun_to_replace = doc['n_tags'][doc['n_chars'].index(first_char)]

    new_title = re.sub(re.escape(noun_to_replace), tag, doc['title'], flags=re.IGNORECASE)
    #print u" -- replacing {0} -> {1}".format(noun_to_replace, tag)
    print u" -- '{0}' and '{1}' -> '{2}'".format(title, doc['title'], new_title)
    print ""
