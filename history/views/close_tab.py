from history.models import Tab, Domain, Page, PageVisit
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from urllib.parse import urlparse
from datetime import timedelta


class CloseTab(APIView):
    """
    Update data when a tab is closed
    """

    def post(self, request, format=None):
        customuser = request.user

        t_id = request.data['tab']
        time = timezone.now()

        try:
            t = Tab.objects.get(tab_id=t_id, closed__isnull=True, owned_by=customuser)
        except Tab.DoesNotExist:
            raise Http404

        d = t.domain_set.filter(closed__isnull=True)

        if d.exists():
            d = d.first()
            d.closed = time
            d.save()
            ta = d.active_times.filter(end__isnull=True)
            if ta.exists():
                ta = ta.first()
                if ta:
                    ta.end = time
                    ta.save()

        t.closed = time
        t.save()

        return Response(status=status.HTTP_200_OK)

class TabUpdate(APIView):
    """
    Make sure that our open tabs match users open tabs
    """
    def post(self, request, format=None):
        cu = request.user

        t_ids = request.data['tab_ids']

        tabs = Tab.objects.filter(closed__isnull=True, owned_by=cu).exclude(tab_id__in=t_ids)

        for t in tabs:
            d = t.domain_set.last()

            if not d.closed:
                d.closed = cu.last_active + timedelta(minutes=15)
                d.save()

            t.closed = cu.last_active + timedelta(minutes=15)
            t.save()

        doms = Domain.objects.filter(closed__isnull=True).exclude(tab__tab_id__in=t_ids)

        for dom in doms:
            dom.closed = cu.last_active + timedelta(minutes=15)
            dom.save()

        time = timezone.now()
        cu.last_active = time
        cu.save()

        return Response(status=status.HTTP_200_OK)
