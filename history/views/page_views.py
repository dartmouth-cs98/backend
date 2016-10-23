<<<<<<< HEAD:history/views.py
from history.models import Category, Page
from history.serializers import CategorySerializer, PageSerializer, UserSerializer
=======
from history.models import Page
from history.serializers import PageSerializer
>>>>>>> 4cbeb61562478bfcf0c14ea4abb62b60472cf271:history/views/page_views.py
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework import permissions, generics

class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class CategoryList(APIView):
    """
    List all code snippets, or create a new snippet.
    """
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get(self, request, format=None):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class PageList(APIView):
    """
    List all Pages, or create a new Page.
    """
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get(self, request, format=None):
        pages = Page.objects.all()
        serializer = PageSerializer(pages, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = PageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class PageDetail(APIView):
    """
    Retrieve, update or delete a Page.
    """
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_object(self, id):
        try:
            return Page.objects.get(id=id)
        except Page.DoesNotExist:
            raise Http404

    def get(self, request, id, format=None):
        page = self.get_object(id)
        serializer = PageSerializer(page)
        return Response(serializer.data)

    def put(self, request, id, format=None):
        page = self.get_object(id)
        serializer = PageSerializer(page, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id, format=None):
        page = self.get_object(id)
        page.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
