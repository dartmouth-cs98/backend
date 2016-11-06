from history.models import Tab, Domain, Page, PageVisit
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from urllib.parse import urlparse


class CloseTab(APIView):
    """
    Update data when a tab is closed
    """

    def post(self, request, format=None):

        t_id = request.data['tab']
        time = timezone.now()

        try:
            t = Tab.objects.get(tab_id=t_id, closed__isnull=True)
        except Tab.DoesNotExist:
            return Response(status=status.HTTP_200_OK)

        d = t.domain_set.filter(closed__isnull=True)

        if d.exists():
            d = d.first()
            d.closed = time
            d.save()
            ta = d.active_times.filter(end__isnull=True)
            if ta.exists():
                ta = ta[0]
                ta.end = time
                ta.save()

        t.closed = time
        t.save()



        return Response(status=status.HTTP_200_OK)
