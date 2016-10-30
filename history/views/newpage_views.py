from history.models import Tab, Domain, Page, PageVisit
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

        t = Tab.objects.filter(tab_id=t_id, closed__isnull=True)
        if t.exists():
            t=t[0]
        else:
            t = Tab(tab_id=t_id)
            t.save()

        domains = t.domain_set.all()

        if domains.filter(base_url=base_url, closed__isnull=True).exists():
            d = domains.get(base_url=base_url, closed__isnull=True)

        else:
            close_domain = domains.filter(closed__isnull=True)

            if close_domain.exists():
                close_domain = close_domain[0]
                ta = close_domain.timeactive_set.get(end__isnull=True)
                ta.end = timezone.now()
                ta.save()
                close_domain.closed = timezone.now()
                close_domain.save()


            d = Domain(title=domain_title, tab=t, base_url=base_url)
            d.save()
            new_ta = TimeActive()
            new_ta.save()
            d.active_times.add(new_ta)

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

        t = Tab.objects.get(tab_id=t_id)

        d = t.domain_set.get(closed__isnull=True)

        ta = TimeActive.objects.get(end__isnull=True)
        ta.end = timezone.now()
        ta.save()

        new_ta = TimeActive()
        new_ta.save()

        d.active_times.add(new_ta)

        return Response(status=status.HTTP_200_OK)
