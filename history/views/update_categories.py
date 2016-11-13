from history.models import Page, Category
from history.serializers import PageSerializer, CategorySerializer
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class CheckPageCategories(APIView):
    """
    Return categories and starred for a page
    """
    def post(self, request, format=None):
        url = request.data['url']

        try:
            p = Page.objects.get(url=url, owned_by=request.user)
        except Page.DoesNotExist:
            return Response(status=status.HTTP_200_OK)

        page = PageSerializer(p)

        return Response(page.data)


class AddCategoryPage(APIView):
    """
    Add Category to Page
    """
    def post(self, request, format=None):
        cat = request.data['category']
        url = request.data['url']

        p = Page.objects.get(url=url, owned_by=request.user)
        c = Category.objects.filter(title=cat, owned_by=request.user)

        if c.exists():
            p.categories.add(c.first())
        else:
            c = Category(title=cat, owned_by=request.user)
            c.save()
            p.categories.add(c)

        serializer = PageSerializer(p)
        return Response(serializer.data)

class DeleteCategoryPage(APIView):
    """
    Delete Category from Page
    """
    def post(self, request, format=None):
        cat = request.data['category']
        url = request.data['url']
        try:
            p = Page.objects.get(url=url, owned_by=request.user)
        except Page.DoesNotExist:
            raise Http404

        c = Category.objects.get(title=cat, owned_by=request.user)

        p.categories.remove(c)

        serializer = PageSerializer(p)
        return Response(serializer.data)

class AddCategory(APIView):
    """
    Add Category
    """
    def post(self, request, format=None):
        cat = request.data['category']
        try:
            c = Category.objects.get(title=cat, owned_by=request.user)
        except Category.DoesNotExist:
            c = Category(title=cat, owned_by=request.user)
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

class UpdateStar(APIView):
    """
    Update Page Star
    """
    def post(self, request, format=None):
        url = request.data['url']
        star = request.data['star']

        try:
            p = Page.objects.get(url=url, owned_by=request.user)
        except Page.DoesNotExist:
            raise Http404

        p.star = star
        p.save()

        serializer = PageSerializer(p)
        return Response(serializer.data)
