from history.models import Tab, Domain, Page, PageVisit, TimeActive
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from urllib.parse import urlparse
from history.common import shorten_url

class NewPage(APIView):
    """
    Handle new page coming in
    """
    def post(self, request, format=None):

        t_id = request.data['tab']
        page_title = request.data['title']
        domain_title = request.data['domain']

        if 'favIconUrl' in request.data.keys():
            favicon = request.data['favIconUrl']
        else:
            favicon = ''

        url = request.data['url']

        if 'previousTabId' in request.data.keys():
            prev_tab = request.data['previousTabId']
        else:
            prev_tab = t_id
        active = request.data['active']
        base_url = urlparse(url).netloc

        # Get the currently active TimeActive (can only be one if exists)
        ta = TimeActive.objects.filter(end__isnull=True)

        # Check if a tab exists with this id that is open in this session
        t = Tab.objects.filter(tab_id=t_id, closed__isnull=True)
        if t.exists():
            t=t[0]
        else:
            if ta.exists() and active:
                ta = ta.first()
                ta.end = timezone.now()
                ta.save()

            if 'chrome://' not in url and 'file:///' not in url and 'chrome-extension://' not in url:
                t = Tab(tab_id=t_id)
                t.save()
            else:
                return Response(status=status.HTTP_200_OK)

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

            if 'chrome://' not in url and 'file:///' not in url and 'chrome-extension://' not in url:
                created = False
                if t_id != prev_tab:
                    prev_t = Tab.objects.filter(tab_id=prev_tab, closed__isnull=True)
                    if prev_t.exists():
                        prev_t = prev_t.first()
                        prev_d = prev_t.domain_set.filter(closed__isnull=True)
                        if prev_d.exists():
                            prev_d = prev_d.first()
                            d = Domain(
                                title=domain_title, tab=t, base_url=base_url,
                                favicon=favicon, opened_from_domain=prev_d,
                                opened_from_tabid=prev_tab
                                )
                            d.save()
                            created = True

                if not created:
                    d = Domain(title=domain_title, tab=t, base_url=base_url, favicon=favicon)
                    d.save()
                if active:
                    new_ta = TimeActive()
                    new_ta.save()
                    d.active_times.add(new_ta)
            else:
                return Response(status=status.HTTP_200_OK)

        short_url = shorten_url(url)

        p = Page.objects.filter(url=short_url)

        if p.exists():
            p = p[0]
            if p.title != page_title:
                p.title = page_title
                p.save()
        else:
            p = Page(title=page_title, url=short_url)
            p.save()

        pv = PageVisit(page=p, domain=d)
        pv.save()
        return Response(status=status.HTTP_201_CREATED)


class UpdateActive(APIView):
    """
    Updates the domain that is active
    """
    def post(self, request, format=None):

        t_id = request.data['tab']
        closed = request.data['closed']

        ta = TimeActive.objects.filter(end__isnull=True)

        if ta.exists():
            ta = ta.first()

        try:
            t = Tab.objects.get(tab_id=t_id, closed__isnull=True)
        except Tab.DoesNotExist:
            if ta and not closed:
                ta.end = timezone.now()
                ta.save()
            return Response(status=status.HTTP_200_OK)



        d = t.domain_set.filter(closed__isnull=True)

        # means that the current page is a chrome:// or file:/// page
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

        new_ta = TimeActive()
        new_ta.save()

        d.active_times.add(new_ta)

        return Response(status=status.HTTP_200_OK)
