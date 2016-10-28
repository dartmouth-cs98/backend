from history.models import Page, Category
from history.serializers import PageSerializer, CategorySerializer
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class AddCategoryPage(APIView):
    """
    Add Category to Page
    """
    def post(self, request, format=None):
        cat = request.data['category']
        url = request.data['url']

        p = Page.objects.get(url=url)
        c = Category.objects.filter(title=cat)

        if c.exists():
            p.categories.add(c.first())
        else:
            c = Category(title=cat)
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
            p = Page.objects.get(url=url)
        except Page.DoesNotExist:
            raise Http404

        c = Category.objects.get(title=cat)

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
            c = Category.objects.get(title=cat)
        except Category.DoesNotExist:
            c = Category(title=cat)
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
            c = Category.objects.get(title=cat)
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
            p = Page.objects.get(url=url)
        except Page.DoesNotExist:
            raise Http404

        p.star = star
        p.save()

        serializer = PageSerializer(p)
        return Response(serializer.data)
