from history.models import Tab, Domain, Page, PageVisit, TimeActive
from authentication.models import CustomUser
from django.utils import timezone
from history.common import shorten_url, create_data, strip_tags, get_count, update_stats, update_timeactive_stats
from history.serializers import PageSerializer
from django.conf import settings
from urllib.parse import urlparse
import requests
from django.db.models import Q
from datetime import timedelta
import os
import json
import ast
from collections import Counter
import operator
from celery import task
from celery.decorators import periodic_task
from celery.task.schedules import crontab
import base64
import ipdb
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@task
def create_page(user_pk, url, base_url, t_id, page_title, domain_title,
                favicon, html, image, prev_tab, active):
    logger.info('LOGGINNG SOMETHING HERE HERE ')

    user = CustomUser.objects.get(pk=user_pk)

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

            update_timeactive_stats(close_domain)

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

    # TODO- gam this is the page where i need to edit?

    p = Page.objects.filter(url=short_url, owned_by=user)

    if p.exists():
        p = p[0]
        p.save()
        if p.title != page_title:
            p.title = page_title
            p.save()
    else:
        p = Page(title=page_title, url=short_url, domain=base_url, owned_by=user)
        #TODO: gam- CHANGE THE NUMBER OF KEY WORDS
        content = strip_tags(html)
        word_counts = get_count(content)
        # word_counts = dict(word_counter)
        sort = sorted(word_counts.items(), key=operator.itemgetter(1))
        sort.reverse()
        sort = sort[0:20]
        # word_counts.reverse()
        # word_counts = word_counts[0:20]
        # first2pairs = {k: word_counts[k] for k in list(word_counts.keys()[:2])}
        # word_counts = word_counts.most_common(20)
        # word_counts = dict(word_counts)
        # logger.info('this is the word coutn dict {0}'.format(word_counts))

        p.keywords = json.dumps(sort)

        logger.info('this is the keyword {0}'.format(p.keywords))
        p.save()




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
    logger.info('got here')

    content = strip_tags(html)

    data = create_data(pv, content)

    logger.info('got here2')


    # uri = settings.SEARCH_BASE_URI + 'pagevisits/pagevisit/' + str(pv.id)
    #
    # requests.put(uri, data=data)

    #TODO: gam- UNCOMMENT UPDATE_STATS
    # update_stats(user, pv)

    logger.info('got to end of func')


    return True


@task
def procrastination_stats(user_pk, base_url):
    user = CustomUser.objects.get(pk=user_pk)

    procr_sites = ast.literal_eval(user.procrastination_sites)

    day = user.day_set.last()

    if base_url in procr_sites:
        day.procrastination_visits = day.procrastination_visits + 1
        day.save()
        return True
    else:
        for p in procr_sites:
            if p in base_url:
                day.procrastination_visits = day.procrastination_visits + 1
                day.save()
                return True

    return False


@periodic_task(run_every=(crontab(hour="7", minute="0", day_of_week="*")),
    ignore_result=True)
def clean_up_db():
    tw = timezone.now() - timedelta(days=14)

    for user in CustomUser.objects.all():
        for pv in user.pagevisit_set.filter(Q(visited__lte=tw)):
            data = create_data(pv, '')

            uri = settings.SEARCH_BASE_URI + 'pagevisits/pagevisit/' + str(pv.id)

            requests.put(uri, data=data)

            # if (pv.page.pagevisit_set
            #     .exclude(s3='https://s3.us-east-2.amazonaws.com/hindsite-production/404_not_found.html')
            #     .count() > 1):
            #     aws_loc = str(user.pk) + '/' + str(pv.pk) + '.html'
            #
            #     settings.S3_CLIENT.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=aws_loc)
            #
            #     pv.s3 = 'https://s3.us-east-2.amazonaws.com/hindsite-production/404_not_found.html'

    return True
