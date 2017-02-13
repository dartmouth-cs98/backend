from history.models import Blacklist, Domain, Page
from history.serializers import BlacklistSerializer
from django.http import Http404
from urllib.parse import urlparse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class CreateBlacklist(APIView):
    """
    Add new blacklist domain
    """
    def post(self, request, format=None):
        cu = request.user

        url = request.data['blacklist']

        if url.startswith('http'):
            base_url = urlparse(url).netloc
        else:
            base_url = url

        b = Blacklist(owned_by=cu, base_url=base_url)
        b.save()

        serializer = BlacklistSerializer(b)

        return Response(serializer.data)

class EditBlacklist(APIView):
    """
    Edit existing blacklist domain
    """
    def post(self, request, format=None):
        cu = request.user

        pk = request.data['pk']
        url = request.data['blacklist']

        if url.startswith('http'):
            base_url = urlparse(url).netloc
        else:
            base_url = url

        try:
            b = Blacklist.objects.get(owned_by=cu, pk=pk)
        except Blacklist.DoesNotExist:
            raise Http404

        b.base_url = base_url
        b.save()

        serializer = BlacklistSerializer(b)

        return Response(serializer.data)

class DeleteBlacklist(APIView):
    """
    Delete blacklist domain
    """
    def post(self, request, format=None):
        cu = request.user

        pk = request.data['pk']

        try:
            b = Blacklist.objects.get(owned_by=cu, pk=pk)
        except Blacklist.DoesNotExist:
            raise Http404

        b.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class SendBlacklists(APIView):
    """
    Send all blacklist domains
    """
    def get(self, request, format=None):
        cu = request.user

        b = cu.blacklist_set.all()

        serializer = BlacklistSerializer(b, many=True)

        return Response(serializer.data)
