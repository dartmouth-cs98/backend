from history.models import Page, Category, TimeActive
from history.serializers import PageSerializer, CategorySerializer, PageInfoSerializer
from django.http import Http404
from urllib.parse import urlparse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from history.common import shorten_url, send_bulk, is_blacklisted
import requests

class CheckPageCategories(APIView):
    """
    Return categories and starred for a page
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

        try:
            p = Page.objects.get(url=short_url, owned_by=request.user)
        except Page.DoesNotExist:
            raise Http404

        page = PageSerializer(p)

        return Response(page.data)

class ActivePageCategories(APIView):
    """
    Return categories and starred for a page
    """
    def get(self, request, format=None):

        try:
            ta = TimeActive.objects.get(end__isnull=True, owned_by=request.user)
        except TimeActive.DoesNotExist:
            return Response(status=status.HTTP_204_NO_CONTENT)

        p = ta.domain_set.first().pagevisit_set.last().page

        page = PageSerializer(p)

        return Response(page.data)


class AddCategoryPage(APIView):
    """
    Add Category to Page
    """
    def post(self, request, format=None):
        cat = request.data['category']
        url = request.data['url']

        if 'color' in request.data.keys():
            color = request.data['color']
        else:
            color = '#F8A055'

        short_url = shorten_url(url)

        try:
            p = Page.objects.get(url=short_url, owned_by=request.user)
        except Page.DoesNotExist:
            page_title = request.data['title']

            if page_title == '':
                page_title = 'No Title'

            base_url = urlparse(url).netloc

            p = Page(title=page_title, url=short_url, domain=base_url, owned_by=user)
            p.save()

        c = Category.objects.filter(title__iexact=cat, owned_by=request.user)

        if c.exists():
            p.categories.add(c.first())
        else:
            c = Category(title=cat, owned_by=request.user, color=color)
            c.save()
            p.categories.add(c)

        pv = p.pagevisit_set.last()
        setattr(p, 'last_visited', pv.visited)
        setattr(p, 's3', pv.s3)
        setattr(p, 'preview', pv.preview)

        serializer = PageInfoSerializer(p)
        return Response(serializer.data)

class DeleteCategoryPage(APIView):
    """
    Delete Category from Page
    """
    def post(self, request, format=None):
        cat = request.data['category']
        url = request.data['url']

        short_url = shorten_url(url)

        try:
            p = Page.objects.get(url=short_url, owned_by=request.user)
        except Page.DoesNotExist:
            raise Http404

        c = Category.objects.get(title=cat, owned_by=request.user)

        p.categories.remove(c)

        pv = p.pagevisit_set.last()
        setattr(p, 'last_visited', pv.visited)
        setattr(p, 's3', pv.s3)
        setattr(p, 'preview', pv.preview)

        serializer = PageInfoSerializer(p)
        return Response(serializer.data)

class AddCategory(APIView):
    """
    Add Category
    """
    def post(self, request, format=None):
        cat = request.data['category']

        if 'color' in request.data.keys():
            color = request.data['color']
        else:
            color = '#F8A055'

        try:
            c = Category.objects.get(title__iexact=cat, owned_by=request.user)
        except Category.DoesNotExist:
            c = Category(title=cat, owned_by=request.user, color=color)
            c.save()

        serializer = CategorySerializer(c)
        return Response(serializer.data)

class DeleteCategory(APIView):
    """
    Delete Category
    """
    def post(self, request, format=None):
        cat = request.data['category']
        try:
            c = Category.objects.get(title=cat, owned_by=request.user)
        except Category.DoesNotExist:
            raise Http404

        c.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class EditCategory(APIView):
    """
    Edit Category
    """
    def post(self, request, format=None):
        old_cat = request.data['old']
        new_cat = request.data['updated']

        try:
            c = Category.objects.get(title=old_cat, owned_by=request.user)
        except Category.DoesNotExist:
            raise Http404

        if 'color' in request.data.keys():
            c.color = request.data['color']

        c.title = new_cat
        c.save()

        serializer = CategorySerializer(c)
        return Response(serializer.data)

class SendCategories(APIView):
    """
    Send all categories for user
    """
    def get(self, request, format=None):
        c = Category.objects.filter(owned_by=request.user)
        serializer = CategorySerializer(c, many=True)
        return Response(serializer.data)

class UpdateStar(APIView):
    """
    Update Page Star
    """
    def post(self, request, format=None):
        url = request.data['url']
        star = request.data['star']

        short_url = shorten_url(url)

        try:
            p = Page.objects.get(url=short_url, owned_by=request.user)
        except Page.DoesNotExist:
            page_title = request.data['title']

            if page_title == '':
                page_title = 'No Title'

            base_url = urlparse(url).netloc

            p = Page(title=page_title, url=short_url, domain=base_url, owned_by=user)

        p.star = star
        p.save()

        serializer = PageSerializer(p)
        return Response(serializer.data)
