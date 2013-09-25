"""Code to update the set of pop sources we use when building dumb headlines.
Note that this code has blocking and CPU-burning chunks all over it, and
isn't meant to be run w/in the tornado process."""

import requests
import re
import nltk
from bs4 import BeautifulSoup


noun_tags = ('NN', 'NNS', 'NNP', 'NNPS')
verb_tags = ('VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ')

def title_tags(title):
    """Checks to see if a given title is usable as a title we can insert
    words into by checking for things like number of words, whether it contains
    nouns, etc."""

    title = title.strip().lower()

    if title.count(" ") < 2:
        return None

    tags = nltk.pos_tag(nltk.word_tokenize(title.lower()))

    long_tags = [t for t in tags if len(t[0]) > 3]

    if len(long_tags) == 0:
        return None

    long_nouns = [t[0] for t in long_tags if t[1] in noun_tags]
    long_verbs = [t[0] for t in long_tags if t[1] in verb_tags]

    tokens = dict()

    if len(long_verbs) > 0:
        tokens['v'] = long_verbs

    if len(long_nouns) > 0:
        tokens['n'] = long_nouns

    return tokens


class PopSource(object):

    def __init__(self, url=None):
        self.url = url
        self.results_encoding = None

    def fetch(self):
        rs = requests.get(self.url)
        if rs.status_code != requests.codes.ok:
            return None
        elif rs.encoding not in ('utf-8', 'UTF-8'):
            return rs.text.encode(rs.encoding.lower())
        else:
            return rs.text

    def filter_match(self, a_match):
        """Hook that subclasses can use to filter out possible matches
        taken from screen scraping regular expressions"""
        return True


class WebSource(PopSource):

    def fetch(self):
        content = super(WebSource, self).fetch()

        if not content:
            return None
        else:
            matches = self.extract_pattern.finditer(content)

            titles = []
            for match in matches:
                groups = match.groups()
                titles.append((groups[0], (groups[1] if len(groups) > 1 else None)))

            valid_titles = []

            for (title, attribution) in titles[:100]:
                tags = title_tags(title)
                if tags:
                    valid_titles.append((title, attribution, tags))
            return valid_titles


class TVShows(WebSource):
    """Fetch a list of popular TV shows from TVGuide."""

    evergreen = False
    source = "TVGuide.com"
    item_type = "Television Show"

    def __init__(self):
        super(TVShows, self).__init__(url="http://www.tvguide.com/top-tv-shows")
        self.extract_pattern = re.compile("<td><a href=\".*?\/tvshows\/.*?\/\d+\">(?P<title>.*?)<\/a><\/td>")


class SongYearSongs(WebSource):

    evergreen = True
    source = "SongYear.com"
    item_type = "Song"

    def __init__(self, year):
        url = "http://www.songyear.com/index.php?year={year}".format(year=year)
        super(SongYearSongs, self).__init__(url=url)
        self.extract_pattern = re.compile("<a href=\"artist\/.*?/title/.*?\">(?P<title>.*?)<\/a>.*? by <a.*?>(?P<attribution>.*?)<\/a>")


class IMDBMovies(WebSource):

    evergreen = True
    source = "IMDB"
    item_type = "Movie"

    def __init__(self, year):
        url = "http://www.imdb.com/year/{year}".format(year=year)
        super(IMDBMovies, self).__init__(url=url)
        self.extract_pattern = re.compile("Dir: <a href=\"\/name\/.*?\/\">(?P<attribution>.*?)<\/a>")

    def fetch(self):
        content = PopSource.fetch(self)
        soup = BeautifulSoup(content, "html.parser")
        results_table = soup.find_all('table', class_="results")[0]
        title_cells = results_table.find_all('td', class_="title")

        matches = []
        for title_cell in title_cells:
            title_as = title_cell.a
            attribute_span = title_cell.find_all('span', class_='credit')
            attribution = self.extract_pattern.search(str(attribute_span[0])).groupdict()['attribution']
            matches.append((title_as.text,
                            attribution))

        valid_titles = []
        for (title, attribution) in matches[:100]:
            tags = title_tags(title)
            if tags:
                valid_titles.append((title, attribution, tags))
        return valid_titles
