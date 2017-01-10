
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
