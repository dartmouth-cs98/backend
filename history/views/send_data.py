from history.models import Tab, Domain, Page, PageVisit, TimeActive, Category
from authentication.models import CustomUser
from django.http import Http404, HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.db.models import Q
from datetime import datetime, timedelta
import pytz
from django.core import serializers
from history.serializers import SendTabSerializer, SendCategorySerializer, SendDomainSerializer
from authentication.serializers import CustomUserSerializer
from django.db.models.functions import Lower
from history.common import blacklist

class SendTabs(APIView):
    """
    Send info for lookback page
    """
    def post(self, request, format=None):
        start = request.data['start']
        end = request.data['end']

        start = pytz.utc.localize(datetime.strptime(start, '%Y-%m-%dT%H:%M:%S.%fZ'))
        end = pytz.utc.localize(datetime.strptime(end, '%Y-%m-%dT%H:%M:%S.%fZ'))

        #domains open during timeframe
        domains = Domain.objects.filter(owned_by=request.user).filter(
                              Q(created__range=[start, end]) |
                              Q(closed__range=[start, end]) |
                              (Q(closed__gte=end) & Q(created__lte=start)) |
                              (Q(created__lte=start) & Q(closed__isnull=True))
                              )

        # pvs = PageVisit.objects.filter(visited__range=[start, end])

        tabs = set()

        for d in domains:
            tabs.add(d.tab)

        domains = list(domains)
        holder = {'tabs': []}

        for t in tabs:
            setattr(t, 'domains', [])

            for d in domains:
                if d.tab == t and d not in t.domains:

                    ta = d.timeactive(start, end)

                    setattr(d, 'pages', d.pagecount)
                    setattr(d, 'minutes_active', ta[0])
                    setattr(d, 'active_times', ta[1])

                    t.domains.append(d)
            holder['tabs'].append(t)

        send = SendTabSerializer(holder)


        return Response(send.data)

class SendCategories(APIView):
    """
    Send categories with their associated pages
    """
    def get(self, request, format=None):
        holder = {'categories': []}

        bl = blacklist(request.user)

        starred = Page.objects.filter(star=True, owned_by=request.user).exclude(domain__in=bl)

        for p in starred:
            pv = p.pagevisit_set.last()
            setattr(p, 'last_visited', pv.visited)
            setattr(p, 'domain', pv.domain.base_url)

        holder['starred'] = starred

        cats = Category.objects.filter(owned_by=request.user).order_by(Lower('title'))

        for c in cats:
            pages = c.page_set.exclude(domain__in=bl)

            for p in pages:
                pv = p.pagevisit_set.last()
                setattr(p, 'last_visited', pv.visited)
                setattr(p, 'domain', pv.domain.base_url)

            setattr(c, 'pages', pages)

            holder['categories'].append(c)

        send = SendCategorySerializer(holder)

        return Response(send.data)

class SendDomain(APIView):
    """
    Send domain and all the pages
    """
    def post(self, request, format=None):
        pk = request.data['pk']

        d = Domain.objects.get(pk=pk, owned_by=request.user)

        pvs = d.pagevisit_set.all().order_by('visited')

        ta = d.timeactive()

        setattr(d, 'pages', d.pagecount)
        setattr(d, 'minutes_active', ta[0])
        setattr(d, 'active_times', ta[1])
        setattr(d, 'pagevisits', pvs)

        send = SendDomainSerializer(d)

        return Response(send.data)

class SendUserData(APIView):
    """
    Send user info
    """
    def get(self, request, format=None):

        cu = request.user

        user = CustomUserSerializer(cu)

        return Response(user.data)
