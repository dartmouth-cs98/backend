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

        holder = {}

        # handle case where start and end time are before and
        # after that day but go through the whole day
        for d in domains:
            c = pvs.filter(domain=d).count()
            ta = d.active_times.filter(Q(start__range=[start, end]) |
                                       Q(end__range=[start, end]))

            minutes_active = 0
            # start = datetime(month=month, day=day, year=year, tzinfo=pytz.UTC)
            # end = datetime(month=month, day=day, year=year, tzinfo=pytz.UTC) + timedelta(days=1)
            for a in ta:
                if a.start < start:
                    time = a.end - start
                elif a.end is None or a.end > end:
                    time = end - a.start
                else:
                    time = a.end - a.start
                minutes_active += int(time.seconds / 60)

            tab = d.tab
            d = serializers.serialize('json', [d])
            d = d[1:len(d)-3]

            d += ', "pages": ' + str(c) + ', '
            d += '"active": ' + serializers.serialize('json', ta, fields=('start', 'end')) + ', '
            d += '"minutes_active": ' + str(minutes_active) + '}}'


            if tab in holder.keys():
                holder[tab].append(d)
            else:
                holder[tab] = [d]
        tabs = []
        for t in holder.keys():
            domains = holder[t]
            tab = serializers.serialize('json', [t])
            tab = tab[1:len(tab)-3]
            d_str = '['
            for d in domains:
                if d is not domains[0]:
                    d_str += ', '
                d_str += d
            d_str += ']'

            tab += ', "domains": ' + d_str + '}}'
            tabs.append(tab)

        response = '['

        for t in tabs:
            if t is not tabs[0]:
                response += ', '
            response += t
        response +=  ']'



        return HttpResponse(response)
        # {"month": 10, "day":30, "year":2016}
