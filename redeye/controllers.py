import tornado.gen
import tornado.template
import tornado.web
import newssources
import random
import motor
import re
import config

VALID_NEWS_TYPES = newssources.sources.keys()
loader = tornado.template.Loader(config.template_dir)

class MainController(tornado.web.RequestHandler):

    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self, news_type=None):
        self.orig_news_type = news_type
        if not news_type:
            news_type = random.choice(VALID_NEWS_TYPES)
        elif news_type not in VALID_NEWS_TYPES:
            raise tornado.web.HTTPError(404, "Invalid news type")

        self.used_news_type = news_type

        newssources.fetch_news(news_type, self._with_news_items)

    @tornado.gen.engine
    def _with_news_items(self, results):
        db = self.settings['db']
        title, tags, link = random.choice(results)
        tag = random.choice(tags)
        first_char = tag[0].lower()
        random_num = random.random()

        query = {
            "n_chars": first_char,
            "rand": {
                "$gte": random_num,
            }
        }
        doc = yield motor.Op(db.pop_sources.find_one, query)

        if not doc:
            doc = yield motor.Op(db.pop_sources.find_one, {
                "n_chars": first_char,
                "rand": {
                    "$lte": random_num,
                }
            })

        noun_to_replace = doc['n_tags'][doc['n_chars'].index(first_char)]

        wapped_tags = ["<em>" + t.lower() + "</em>" for t in tags]

        if len(wapped_tags) == 1:
            tags_formatted = wapped_tags[0]
        else:
            tags_formatted = ", ".join(wapped_tags[:-1]) + " and " + wapped_tags[-1]

        replace_esc = re.escape(noun_to_replace)

        new_title = re.sub(replace_esc, tag, doc['title'], count=1, flags=re.IGNORECASE)
        em_title = re.sub(replace_esc, u"<strong>" + tag + u"</strong>", doc['title'], count=1, flags=re.IGNORECASE)

        params = {
            "new_title": new_title,
            "used_news_type": self.used_news_type,
            "selected_news_type": self.orig_news_type,
            "news_title": title,
            "news_title_em": em_title,
            "news_link": link,
            "news_types": VALID_NEWS_TYPES,
            "config": config,
            "pop_title": doc['title'],
            "pop_tags": tags_formatted,
            "pop": doc
        }

        html = loader.load("news.html").generate(**params)
        self.write(html)
        self.finish()
