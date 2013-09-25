import random
import re

def generate_title(tag, db):

    first_char = tag[0].lower()

    doc = db.pop_collection.find_one({
        "n_chars": first_char,
        "rand": {
            "$gte": random.random(),
        }
    })

    if not doc:
        doc = db.pop_collection.find_one({
            "n_chars": first_char,
            "rand": {
                "$lte": random.random(),
            }
        })

    noun_to_replace = doc['n_tags'][doc['n_chars'].index(first_char)]

    new_title = re.sub(re.escape(noun_to_replace), tag, doc['title'], flags=re.IGNORECASE)
    return new_title
