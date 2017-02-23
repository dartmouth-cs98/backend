from search.common import datetime_formatter
from bs4 import BeautifulSoup

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

def strip_tags(html):
    soup = BeautifulSoup(html, 'html.parser')
    content = ''

    for a in soup.find_all(['div', 'a', 'p', 'title', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'li', 'ol', 'span', 'strong', 'td', 'th']):
        for s in a.strings:
            content += s + ' '
    content = content.replace('\n', ' ').replace("\\n", ' ').replace("\'", "'").replace("\\t", " ").replace("\\r", ' ').replace(u'\xa0', u' ')

    return content

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
