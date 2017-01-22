from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from history.models import PageVisit
from history.serializers import PageVisitSerializer
import json
import requests

class BasicSearch(APIView):

    def post(self, request, format=None):

        cu = request.user
        search_query = request.data['query']

        uri = settings.SEARCH_BASE_URI + 'pagevisits/_search'

        query = json.dumps({
          "query": {
            "bool": {
              "must": [
                {
                  "match": {
                    "user_id": cu.id
                  }
                }
              ],
              "should": [
                {
                  "multi_match": {
                    "query": search_query,
                    "fields": [
                      "title",
                      "html"
                    ]
                  }
                }
              ]
            }
          }
        })

        response = requests.get(uri, data=query)
        results = json.loads(response.text)

        hits = []

        for hit in results['hits']['hits']:
            hits.append(int(hit['_id']))

        pvs = PageVisit.objects.filter(id__in=hits)

        send = PageVisitSerializer(pvs, many=True)

        return Response(send.data)
