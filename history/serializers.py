from rest_framework import serializers
from history.models import Category, Page


class CategorySerializer(serializers.Serializer):
    pk = serializers.IntegerField()
    title = serializers.CharField(max_length=1000)


class PageSerializer(serializers.Serializer):
    # class Meta:
    #     model = Page
    #     fields = ('id', 'title', 'url', 'star', 'categories', 'created')
    pk = serializers.IntegerField(read_only=True)
    title = serializers.CharField(required=True, allow_blank=False, max_length=100)
    url = serializers.CharField(required=True, allow_blank=False, max_length=1000)
    star = serializers.BooleanField()
    categories = CategorySerializer(many=True)
    created = serializers.DateTimeField()

    def create(self, validated_data):
        """
        Create and return a new `Category` instance, given the validated data.
        """
        category_data = validated_data.pop('categories')
        p = Page.objects.create(**validated_data)
        for c in category_data:
            cat = Category.objects.filter(title=c['title'])
            if cat:
                p.categories.add(cat[0])
            else:
                cat = Category.objects.create(**c)
                p.categories.add(cat)
        p.save()
        return p

    def update(self, instance, validated_data):
        """
        Update and return an existing `Category` instance, given the validated data.
        """
        instance.title = validated_data.get('title', instance.title)
        instance.url = validated_data.get('url', instance.url)
        instance.star = validated_data.get('star', instance.star)
        instance.save()
        return instance

class CategoryPageSerializer(serializers.Serializer):
    pk = serializers.IntegerField()
    title = serializers.CharField(max_length=1000)
    pages = PageSerializer(many=True)

class SendCategorySerializer(serializers.Serializer):
    categories = CategoryPageSerializer(many=True)
    starred = PageSerializer(many=True)

class TimeActiveSerializer(serializers.Serializer):
    start = serializers.DateTimeField()
    end = serializers.DateTimeField()

class DomainSerializer(serializers.Serializer):
    pk = serializers.IntegerField()
    base_url = serializers.CharField(max_length=1000)
    created = serializers.DateTimeField()
    closed = serializers.DateTimeField()
    title = serializers.CharField(max_length=1000)
    favicon = serializers.CharField(max_length=1000)
    active_times = TimeActiveSerializer(many=True)
    pages = serializers.IntegerField()
    opened_from_domain = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    opened_from_tabid = serializers.IntegerField()
    minutes_active = serializers.IntegerField()

class TabSerializer(serializers.Serializer):
    domains = DomainSerializer(many=True)
    tab_id = serializers.IntegerField()

class SendTabSerializer(serializers.Serializer):
    tabs = TabSerializer(many=True)

class PageVisitSerializer(serializers.Serializer):
    page = PageSerializer()

class SendDomainSerializer(serializers.Serializer):
    pk = serializers.IntegerField()
    base_url = serializers.CharField(max_length=1000)
    created = serializers.DateTimeField()
    closed = serializers.DateTimeField()
    title = serializers.CharField(max_length=1000)
    favicon = serializers.CharField(max_length=1000)
    active_times = TimeActiveSerializer(many=True)
    pages = serializers.IntegerField()
    minutes_active = serializers.IntegerField()
    pagevisits = PageVisitSerializer(many=True)
