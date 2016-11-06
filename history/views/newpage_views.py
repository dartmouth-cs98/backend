from history.models import Tab, Domain, Page, PageVisit, TimeActive
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from urllib.parse import urlparse


class NewPage(APIView):
    """
    Handle new page coming in
    """
    def post(self, request, format=None):

        t_id = request.data['tab']
        page_title = request.data['title']
        domain_title = request.data['domain']
        url = request.data['url']
        base_url = urlparse(url).netloc

        # Get the currently active TimeActive (can only be one if exists)
        ta = TimeActive.objects.filter(end__isnull=True)
        if ta.exists():
            ta = ta.first()

        # Check if a tab exists with this id that is open in this session
        t = Tab.objects.filter(tab_id=t_id, closed__isnull=True)
        if t.exists():
            t=t[0]
        else:
            if ta:
                ta.end = timezone.now()
                ta.save()

            if 'chrome://' not in url and 'file:///' not in url:
                t = Tab(tab_id=t_id)
                t.save()
            else:
                return Response(status=status.HTTP_200_OK)

        domains = t.domain_set.all()

        if domains.filter(base_url=base_url, closed__isnull=True).exists():
            d = domains.get(base_url=base_url, closed__isnull=True)

        else:
            close_domain = domains.filter(closed__isnull=True)

            if close_domain.exists():
                close_domain = close_domain[0]
                ta.end = timezone.now()
                ta.save()
                close_domain.closed = timezone.now()
                close_domain.save()

            if 'chrome://' not in url and 'file:///' not in url:
                d = Domain(title=domain_title, tab=t, base_url=base_url)
                d.save()
                new_ta = TimeActive()
                new_ta.save()
                d.active_times.add(new_ta)
            else:
                return Response(status=status.HTTP_200_OK)

        p = Page.objects.filter(url=url)

        if p.exists():
            p = p[0]
        else:
            p = Page(title=page_title, url=url)
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

        ta = TimeActive.objects.filter(end__isnull=True)

        if ta.exists():
            ta = ta[0]

        try:
            t = Tab.objects.get(tab_id=t_id)
        except Tab.DoesNotExist:
            if ta:
                ta.end = timezone.now()
                ta.save()
            return Response(status=status.HTTP_200_OK)



        d = t.domain_set.filter(closed__isnull=True)

        # means that the current page is a chrome:// or file:/// page
        if not d.exists():
            if ta:
                ta.end = timezone.now()
                ta.save()
            return Response(status=status.HTTP_200_OK)

        if ta:
            ta.end = timezone.now()
            ta.save()

        new_ta = TimeActive()
        new_ta.save()

        d.active_times.add(new_ta)

        return Response(status=status.HTTP_200_OK)
