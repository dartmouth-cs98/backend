from history.models import Category
from history.serializers import CategorySerializer
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class CategoryList(APIView):
    """
    List all Categories, or create a new Category.
    """
    def get(self, request, format=None):
        cats = Category.objects.all()
        serializer = CategorySerializer(cats, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryDetail(APIView):
    """
    Retrieve, update or delete a Category.
    """
    def get_object(self, id):
        try:
            return Category.objects.get(id=id)
        except Page.DoesNotExist:
            raise Http404

    def get(self, request, id, format=None):
        cat = self.get_object(id)
        serializer = CategorySerializer(cat)
        return Response(serializer.data)

    def put(self, request, id, format=None):
        cat = self.get_object(id)
        serializer = CategorySerializer(cat, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id, format=None):
        cat = self.get_object(id)
        cat.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
