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
from history.serializers import (
        SendTabSerializer, SendCategorySerializer,
        SendDomainSerializer, PopupInfoSerializer,
        NewSendCategorySerializer
        )
from authentication.serializers import UserInfoSerializer
from django.db.models.functions import Lower
from history.common import blacklist
from urllib.parse import urlparse
from history.common import shorten_url, send_bulk, is_blacklisted


class SendPopupInfo(APIView):
    """
    Return all data for popup
    """
    def post(self, request, format=None):
        url = request.data['url']

        url = request.data['url']
        base_url = urlparse(url).netloc

        if is_blacklisted(request.user, base_url):
            return Response({
                'status': 'Blacklist',
                'message': 'This page is blacklisted.'
            }, status=status.HTTP_204_NO_CONTENT)

        short_url = shorten_url(url)

        c = Category.objects.filter(owned_by=request.user)

        holder = {'categories': c, 'tracking': request.user.tracking_on}

        try:
            p = Page.objects.get(url=short_url, owned_by=request.user)
        except Page.DoesNotExist:
            holder['page'] = None
            send = PopupInfoSerializer(holder)
            return Response(send.data, status=status.HTTP_404_NOT_FOUND)

        holder['page'] = p

        send = PopupInfoSerializer(holder)

        return Response(send.data)

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
            setattr(p, 's3', pv.s3)

        holder['starred'] = starred

        cats = Category.objects.filter(owned_by=request.user).order_by(Lower('title'))

        for c in cats:
            pages = c.page_set.exclude(domain__in=bl)

            for p in pages:
                pv = p.pagevisit_set.last()
                setattr(p, 'last_visited', pv.visited)
                setattr(p, 'domain', pv.domain.base_url)
                setattr(p, 's3', pv.s3)

            setattr(c, 'pages', pages)

            holder['categories'].append(c)

        send = SendCategorySerializer(holder)

        return Response(send.data)

class NewSendCategories(APIView):

    def get(self, request, format=None):
        holder = {'categories': []}

        bl = blacklist(request.user)

        page_list = []

        starred = Page.objects.filter(star=True, owned_by=request.user).exclude(domain__in=bl)
        starred_pks = []

        for p in starred:
            cat_pks = []

            for category in p.categories.all():
                cat_pks.append(category.pk)

            pv = p.pagevisit_set.last()
            setattr(p, 'last_visited', pv.visited)
            setattr(p, 'domain', pv.domain.base_url)
            setattr(p, 's3', pv.s3)
            setattr(p, 'cat_pks', cat_pks)

            page_list.append(p)
            starred_pks.append(p.pk)

        holder['starred'] = starred_pks

        cats = Category.objects.filter(owned_by=request.user).order_by(Lower('title'))

        for c in cats:
            pages = c.page_set.exclude(domain__in=bl)
            page_pks = []
            for p in pages:
                cat_pks = []
                for category in p.categories.all():
                    cat_pks.append(category.pk)

                pv = p.pagevisit_set.last()
                setattr(p, 'last_visited', pv.visited)
                setattr(p, 'domain', pv.domain.base_url)
                setattr(p, 's3', pv.s3)
                setattr(p, 'cat_pks', cat_pks)

                page_pks.append(p.pk)
                page_list.append(p)

            setattr(c, 'pages', page_pks)

            holder['categories'].append(c)

        holder['pages'] = list(set(page_list))

        send = NewSendCategorySerializer(holder)

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

        user = UserInfoSerializer(cu)

        return Response(user.data)
