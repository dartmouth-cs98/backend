from history.models import Tab, Domain, Page, PageVisit, TimeActive
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from urllib.parse import urlparse
from django.conf import settings
from history.common import is_blacklisted
import time
from history.utils import create_page_login
from history.tasks import create_page, procrastination_stats


class NewPage(APIView):
    """
    Handle new page coming in
    """
    def post(self, request, format=None):
        user = request.user

        if not user.tracking_on:
            return Response({
                'status': 'Tracking Off',
                'message': 'hindsite is not currently tracking your history'
            })

        url = request.data['url']
        base_url = urlparse(url).netloc

        procrastination_stats.delay(user.pk, base_url)

        if is_blacklisted(user, base_url):
            return Response({
                'status': 'Blacklist',
                'message': 'This page is blacklisted.'
            })

        t_id = request.data['tab']
        page_title = request.data['title']
        domain_title = request.data['domain']

        if page_title == '':
            page_title = 'No Title'


        if 'favIconUrl' in request.data.keys():
            favicon = request.data['favIconUrl']
        else:
            favicon = ''

        if 'html' in request.data.keys():
            html = request.data['html']
        else:
            html = ''

        if 'image' in request.data.keys():
            image = request.data['image'].split(',')[1]
        else:
            image = ''

        if 'previousTabId' in request.data.keys():
            prev_tab = request.data['previousTabId']
        else:
            prev_tab = t_id
        active = request.data['active']

        if 'login' in request.data.keys():
            login = request.data['login']
        else:
            login = False

        if login:
            page = create_page_login(user, url, base_url, t_id,
                         page_title, domain_title, favicon, html,
                         image, prev_tab, active)

            if page:
                return Response(page.data)
        else:
            create_page.delay(user.pk, url, base_url, t_id,
                             page_title, domain_title, favicon, html,
                             image, prev_tab, active)

        return Response()


class UpdateActive(APIView):
    """
    Updates the domain that is active
    """
    def post(self, request, format=None):
        user = request.user

        if not user.tracking_on:
            return Response({
                'status': 'Tracking Off',
                'message': 'hindsite is not currently tracking your history'
            })

        t_id = request.data['tab']
        if 'closed' in request.data.keys():
            closed = request.data['closed']
        else:
            closed = False

        ta = TimeActive.objects.filter(end__isnull=True, owned_by=user)

        try:
            t = Tab.objects.get(tab_id=t_id, closed__isnull=True, owned_by=user)
        except Tab.DoesNotExist:
            url = request.data['url']
            base_url = urlparse(url).netloc

            if ('https://goo.gl/' in url or 'hindsite-local' in url or
                    'hindsite-production' in url or 'chrome://' in url or
                    'file:///' in url or 'chrome-extension://' in url):
                return Response()


            if is_blacklisted(user, base_url):
                return Response({
                    'status': 'Blacklist',
                    'message': 'This page is blacklisted.'
                })

            if ('html' not in request.data.keys()
                    and 'title' not in request.data.keys()
                    and 'domain' not in request.data.keys()):
                raise Http404


            if ta.exists() and not closed:
                timeactive = ta.first()
                timeactive.end = timezone.now()
                timeactive.save()

            if 'title' in request.data.keys():
                page_title = request.data['title']
            else:
                page_title = 'No Title'

            domain_title = request.data['domain']


            if 'favIconUrl' in request.data.keys():
                favicon = request.data['favIconUrl']
            else:
                favicon = ''

            if 'html' in request.data.keys():
                html = request.data['html']
            else:
                html = ''

            if 'image' in request.data.keys():
                image = request.data['image'].split(',')[1]
            else:
                image = ''

            if 'previousTabId' in request.data.keys():
                prev_tab = request.data['previousTabId']
            else:
                prev_tab = t_id
            active = request.data['active']

            create_page.delay(user.pk, url, base_url, t_id,
                                 page_title, domain_title, favicon, html,
                                 image, prev_tab, active)

            return Response(status=status.HTTP_200_OK)



        d = t.domain_set.filter(closed__isnull=True)

        # means that the current page is a chrome:// or file:/// or blacklisted page
        if not d.exists():
            if ta.exists() and not closed:
                timeactive = ta.first()
                timeactive.end = timezone.now()
                timeactive.save()
            return Response(status=status.HTTP_200_OK)
        else:
            d = d.first()

        if ta.exists() and not closed:
            timeactive = ta.first()
            timeactive.end = timezone.now()
            timeactive.save()

        new_ta = TimeActive(owned_by=user)
        new_ta.save()

        d.active_times.add(new_ta)

        return Response(status=status.HTTP_200_OK)
