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
# from history.utils import create_page
from history.tasks import create_page

class NewPage(APIView):
    """
    Handle new page coming in
    """
    def post(self, request, format=None):
        user = request.user

        url = request.data['url']
        base_url = urlparse(url).netloc

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
            fav_d = Domain.objects.filter(base_url=base_url).exclude(favicon='').last()
            if fav_d:
                favicon = fav_d.favicon
            else:
                favicon = ''

        if 'html' in request.data.keys():
            html = request.data['html']
        else:
            html = ''

        if 'previousTabId' in request.data.keys():
            prev_tab = request.data['previousTabId']
        else:
            prev_tab = t_id
        active = request.data['active']

        if 'login' in request.data.keys():
            login = request.data['login']
        else:
            login = False


        # page = create_page(user, url, base_url, t_id,
        #              page_title, domain_title, favicon, html,
        #              prev_tab, active)


        create_page.delay(user.pk, url, base_url, t_id,
                             page_title, domain_title, favicon, html,
                             prev_tab, active)

        # if login and page:
        #     return Response(page.data)


        return Response()


class UpdateActive(APIView):
    """
    Updates the domain that is active
    """
    def post(self, request, format=None):
        user = request.user
        t_id = request.data['tab']
        closed = request.data['closed']

        ta = TimeActive.objects.filter(end__isnull=True, owned_by=user)

        if ta.exists():
            ta = ta.first()

        try:
            t = Tab.objects.get(tab_id=t_id, closed__isnull=True, owned_by=user)
        except Tab.DoesNotExist:
            if ta and not closed:
                ta.end = timezone.now()
                ta.save()
            url = request.data['url']
            base_url = urlparse(url).netloc

            if is_blacklisted(user, base_url):
                return Response({
                    'status': 'Blacklist',
                    'message': 'This page is blacklisted.'
                })

            page_title = request.data['title']
            domain_title = request.data['domain']


            if 'favIconUrl' in request.data.keys():
                favicon = request.data['favIconUrl']
            else:
                favicon = ''

            if 'html' in request.data.keys():
                html = request.data['html']
            else:
                html = ''

            if 'previousTabId' in request.data.keys():
                prev_tab = request.data['previousTabId']
            else:
                prev_tab = t_id
            active = request.data['active']

            # job = django_rq.enqueue(create_page, user, url, base_url, t_id,
            #                             page_title, domain_title, favicon, html,
            #                             prev_tab, active)

            create_page(user, url, base_url, t_id,
                         page_title, domain_title, favicon, html,
                         prev_tab, active)

            return Response(status=status.HTTP_200_OK)



        d = t.domain_set.filter(closed__isnull=True)

        # means that the current page is a chrome:// or file:/// or blacklisted page
        if not d.exists():
            if ta and not closed:
                ta.end = timezone.now()
                ta.save()
            return Response(status=status.HTTP_200_OK)
        else:
            d = d.first()

        if ta and not closed:
            ta.end = timezone.now()
            ta.save()

        new_ta = TimeActive(owned_by=user)
        new_ta.save()

        d.active_times.add(new_ta)

        return Response(status=status.HTTP_200_OK)
