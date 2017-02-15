from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from history.models import PageVisit, Page
from history.serializers import PageVisitSerializerNoHTML, PageVisitSerializer
from django.db.models import Case, When
from search.common import datetime_formatter
import json
import requests

class GetHTML(APIView):

    def post(self, request, format=None):
        cu = request.user

        pk = request.data['pk']

        if 'page' in request.data.keys():
            is_page = request.data['page']
        else:
            is_page = False

        if not is_page:
            try:
                pv = PageVisit.objects.get(owned_by=cu, pk=pk)
            except PageVisit.DoesNotExist:
                raise Http404
        else:
            try:
                page = Page.objects.get(owned_by=cu, pk=pk)
            except PageVisit.DoesNotExist:
                raise Http404

            pv = page.pagevisit_set.last()

        result = PageVisitSerializer(pv)

        return Response(result.data)


class Search(APIView):

    def post(self, request, format=None):

        cu = request.user
        search_query = request.data['query']

        if 'start_time' in request.data.keys():
            start_time = request.data['start_time']
        else:
            start_time = "now-24M"

        if 'end_time' in request.data.keys():
            end_time = request.data['end_time']
        else:
            end_time = "now"

        if 'category' in request.data.keys():
            cat = [request.data['category']]
        else:
            cat = []

        if 'order' in request.data.keys():
            order = request.data['order']
        else:
            order = 'relevance'

        uri = settings.SEARCH_BASE_URI + 'pagevisits/_search/'


        query = json.dumps({
            "_source": ["_id"],
            "size": 40,
            "query": {
                "bool": {
                    "must": {
                        "range": {
                            "date": {
                                "gte": start_time,
                                "lte": end_time
                            }
                        }
                    },
                    "should": {
                        "multi_match": { "query": search_query, "fields": ["title","html"] }
                    },
                    "filter": {
                        "term" : {"user_id" : cu.id}
                    }
                }
            }
        })

        response = requests.get(uri, data=query)
        results = json.loads(response.text)

        hits = []

        for hit in results['hits']['hits']:
            hits.append(int(hit['_id']))

        preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(hits)])

        if len(cat)>0:
            unique_pvs = PageVisit.objects.filter(pk__in=hits, page__categories__title__in=cat).order_by('page_id').distinct('page_id')
        else:
            unique_pvs = PageVisit.objects.filter(pk__in=hits).order_by('page_id').distinct('page_id')

        if order == 'relevance':
            pvs = PageVisit.objects.filter(pk__in=[pv.pk for pv in unique_pvs]).order_by(preserved)
        elif order == 'date':
            pvs = PageVisit.objects.filter(pk__in=[pv.pk for pv in unique_pvs])
        else:
            pvs = PageVisit.objects.filter(pk__in=[pv.pk for pv in unique_pvs]).order_by(preserved)

        send = PageVisitSerializerNoHTML(pvs, many=True)

        return Response(send.data)
