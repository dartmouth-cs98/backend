from html.parser import HTMLParser
from search.common import datetime_formatter

def shorten_url(url):
    import requests
    import json

    google_url = 'https://www.googleapis.com/urlshortener/v1/url?key=AIzaSyAyNJpylrKrx1dy2iss__bSshi2W-nl77c'
    data = {'longUrl': url}
    headers = {'Content-Type': 'application/json'}

    resp = requests.post(google_url, data=json.dumps(data), headers=headers)
    if resp.ok:
        return resp.json()['id']
    else:
        return url

# http://stackoverflow.com/questions/753052/strip-html-from-strings-in-python

class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.fed = ''
        self.strict = False
    def handle_data(self, d):
        self.fed +=' ' + d
    def get_data(self):
        return self.fed

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


def create_data(pv):
    import json

    return json.dumps({
        "user_id": pv.owned_by.id,
        "title": pv.page.title,
        "html": strip_tags(pv.html),
        "date": datetime_formatter(pv.visited)
    })

def create_action(pv):
    import json

    return json.dumps({
        "index": {
            "_index" : pv._meta.verbose_name_plural, "_type": pv._meta.verbose_name, "_id": str(pv.id)
        }
    })

def create_bulk(pvs):
    data = ''

    for pv in pvs:
        data += create_action(pv) + '\n' + create_data(pv) + '\n'

    return data

def send_bulk(pvs):
    from django.conf import settings
    import requests
    import json

    uri = settings.SEARCH_BASE_URI + '_bulk/'

    data = create_bulk(pvs)

    response = requests.post(uri, data=data)
    results = json.loads(response.text)
    return results


def is_blacklisted(user, domain):

    blacklist = []

    for b in user.blacklist_set.all():
        blacklist.append(b.base_url)
        if b.base_url.startswith('www.'):
            blacklist.append(b.base_url[4:])

    return domain in blacklist

def blacklist(user):
    blacklist = []

    for b in user.blacklist_set.all():
        blacklist.append(b.base_url)
        if b.base_url.startswith('www.'):
            blacklist.append(b.base_url[4:])

    return blacklist
