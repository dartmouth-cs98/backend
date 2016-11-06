from history.models import Tab, Domain, Page, PageVisit, TimeActive
from django.http import Http404, HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.db.models import Q
from datetime import datetime, timedelta
import pytz
from django.core import serializers
from history.serializers import SendTabSerializer

class SendTabs(APIView):
    """
    Send info for lookback page
    """
    def post(self, request, format=None):
        start = request.data['start']
        end = request.data['end']

        start = pytz.utc.localize(datetime.strptime(start, '%Y-%m-%dT%H:%M:%S.%fZ'))
        end = pytz.utc.localize(datetime.strptime(end, '%Y-%m-%dT%H:%M:%S.%fZ'))

        pvs = PageVisit.objects.filter(visited__range=[start, end])

        domains = set()
        tabs = set()

        for pv in pvs:
            domains.add(pv.domain)
            tabs.add(pv.domain.tab)

        domains = list(domains)
        holder = {'tabs': []}

        for t in tabs:
            setattr(t, 'domains', [])

            for d in domains:
                if d.tab == t and d not in t.domains:

                    c = pvs.filter(domain=d).count()

                    # handle case where start and end time are before and
                    # after that day but go through the whole day
                    ta = d.active_times.filter(Q(start__range=[start, end]) |
                                               Q(end__range=[start, end]))

                    minutes_active = 0

                    for a in ta:
                        if a.start < start:
                            time = a.end - start
                        elif a.end is None or a.end > end:
                            time = end - a.start
                        else:
                            time = a.end - a.start
                        minutes_active += int(time.seconds / 60)

                    setattr(d, 'pages', c)
                    setattr(d, 'active_times', ta)
                    setattr(d, 'minutes_active', minutes_active)

                    t.domains.append(d)
            holder['tabs'].append(t)

        send = SendTabSerializer(holder)


        return Response(send.data)
