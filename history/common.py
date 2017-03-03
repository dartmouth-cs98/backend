from search.common import datetime_formatter
from bs4 import BeautifulSoup
import re
from collections import Counter
import operator
from hindsite.constants import ignore_words

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

    for a in soup.find_all(['div','a', 'p', 'title', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'li', 'ol', 'span', 'strong', 'td', 'th']):
            for s in a.strings:
                if (s.find('function(')==-1 and s.find('image/jpeg')==-1 and
                        s.find('image/png')==-1 and s.find('image/jpg')==-1 and
                        s.find('image/gif')==-1 and s.find('{')==-1 and
                        s.find('document.get')==-1):
                    content += s + ' '

    content = content.replace('\\n', ' ').replace("\n", ' ').replace("\\'", "'").replace("\'", "'").replace("\\t", " ").replace("\\r", ' ').replace('*', ' ')
    content = content.replace('. ', ' ').replace(',', '').replace('"', '').replace('!', '').replace('?', '').replace('(', '').replace(')', '').replace(':', '')
    content = content.replace(';', '').replace('[', '').replace(']', '')
    content = re.sub(r'[^\x00-\x7F]+',' ', content)

    return content

def get_count(content):
    content = content.lower().split()
    slim_sum = [word for word in content if word not in ignore_words]
    counts = Counter(slim_sum)

    return counts

def create_data(pv, content):
    import json

    return json.dumps({
        "user_id": pv.owned_by.id,
        "title": pv.page.title,
        "html": content,
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
