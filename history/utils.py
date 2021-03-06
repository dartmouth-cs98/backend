from history.models import Tab, Domain, Page, PageVisit, TimeActive
from django.utils import timezone
from history.common import shorten_url, create_data, strip_tags, get_count, update_stats
from history.serializers import PageSerializer
from django.conf import settings
from urllib.parse import urlparse
import requests
from django.db.models import Q
from datetime import timedelta
import os
import json
import base64
from collections import Counter

def create_page_login(user, url, base_url, t_id, page_title, domain_title,
                favicon, html, image, prev_tab, active):


    if favicon == '':
        fav_d = Domain.objects.filter(base_url=base_url).exclude(favicon='').last()
        if fav_d:
            favicon = fav_d.favicon

    # Get the currently active TimeActive (can only be one if exists)
    ta = TimeActive.objects.filter(end__isnull=True, owned_by=user)

    # Check if a tab exists with this id that is open in this session
    t = Tab.objects.filter(tab_id=t_id, closed__isnull=True, owned_by=user)
    if t.exists():
        t=t[0]
    else:
        if ta.exists() and active:
            ta = ta.first()
            ta.end = timezone.now()
            ta.save()

        if ('https://goo.gl/' not in url and 'hindsite-local' not in url and
                'hindsite-production' not in url and 'chrome://' not in url and
                'file:///' not in url and 'chrome-extension://' not in url):
            t = Tab(tab_id=t_id, owned_by=user)
            t.save()
        else:
            return False

    domains = t.domain_set.all()

    if domains.filter(base_url=base_url, closed__isnull=True).exists():
        d = domains.get(base_url=base_url, closed__isnull=True)
        if favicon != '' and favicon != d.favicon:
            d.favicon = favicon
            d.save()
    else:
        close_domain = domains.filter(closed__isnull=True)

        if close_domain.exists():
            close_domain = close_domain[0]
            if ta.exists():
                ta = ta.first()
                ta.end = timezone.now()
                ta.save()
            close_domain.closed = timezone.now()
            close_domain.save()

        if ('https://goo.gl/' not in url and 'hindsite-local' not in url and
                'hindsite-production' not in url and 'chrome://' not in url and
                'file:///' not in url and 'chrome-extension://' not in url):
            created = False
            if t_id != prev_tab:
                prev_t = Tab.objects.filter(tab_id=prev_tab, closed__isnull=True, owned_by=user)
                if prev_t.exists():
                    prev_t = prev_t.first()
                    prev_d = prev_t.domain_set.filter(closed__isnull=True)
                    if prev_d.exists():
                        prev_d = prev_d.first()
                        d = Domain(
                            title=domain_title, tab=t, base_url=base_url,
                            favicon=favicon, opened_from_domain=prev_d,
                            opened_from_tabid=prev_tab, owned_by=user
                            )
                        d.save()
                        created = True

            if not created:
                d = Domain(title=domain_title, tab=t, base_url=base_url, favicon=favicon, owned_by=user)
                d.save()
            if active:
                new_ta = TimeActive(owned_by=user)
                new_ta.save()
                d.active_times.add(new_ta)
        else:
            return False

    short_url = shorten_url(url)

    p = Page.objects.filter(url=short_url, owned_by=user)

    if p.exists():
        p = p[0]
        if p.title != page_title:
            p.title = page_title
            p.save()
    else:
        p = Page(title=page_title, url=short_url, domain=base_url, owned_by=user)
        p.save()

    pv = PageVisit(page=p, domain=d, owned_by=user)

    session = user.session_set.filter(active=True)

    if session.exists():
        session = session.first()
        if session.end:
            if session.end < timezone.now():
                pv.session = session
            else:
                session.active = False
                session.save()
        else:
            pv.session = session

    pv.save()

    if len(html) > 0:
        aws_loc = str(user.pk) + '/' + str(pv.pk) + '.html'

        # No encryption
        # settings.S3_CLIENT.put_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME,
        #                             Key=aws_loc, Body=html, ContentType='text/html')

        # Encryption
        settings.S3_CLIENT.put_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                                    Key=aws_loc, Body=html, SSECustomerKey=user.key,
                                    SSECustomerAlgorithm='AES256', ContentType='text/html')

        pv.s3 = settings.AWS_BUCKET_URL + aws_loc

    if len(image) > 0:
        img_loc = str(user.pk) + '/' + str(pv.pk) + '.jpg'

        bits = base64.b64decode(image)

        settings.S3_CLIENT.put_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                                    Key=img_loc, Body=bits, SSECustomerKey=user.key,
                                    SSECustomerAlgorithm='AES256', ContentType='image/jpeg')

        pv.preview = settings.AWS_BUCKET_URL + img_loc

    pv.save()

    content = strip_tags(html)

    data = create_data(pv, content)

    uri = settings.SEARCH_BASE_URI + 'pagevisits/pagevisit/' + str(pv.id)

    requests.put(uri, data=data)

    update_stats(user, pv)

    page = PageSerializer(p)
    
    return page
