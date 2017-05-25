from rest_framework import serializers
from history.models import Category, Page


class CategorySerializer(serializers.Serializer):
    pk = serializers.IntegerField()
    title = serializers.CharField(max_length=1000)
    color = serializers.CharField(max_length=7)
    keywords = serializers.CharField(default='{}')



class PageSerializer(serializers.Serializer):
    pk = serializers.IntegerField(read_only=True)
    title = serializers.CharField(required=True, allow_blank=False)
    url = serializers.CharField(required=True, allow_blank=False, max_length=1000)
    star = serializers.BooleanField()
    note = serializers.CharField()
    categories = CategorySerializer(many=True)
    created = serializers.DateTimeField()
    keywords = serializers.CharField(default='{}')


class PageInfoSerializer(serializers.Serializer):
    pk = serializers.IntegerField(read_only=True)
    title = serializers.CharField(required=True, allow_blank=False)
    url = serializers.CharField(required=True, allow_blank=False, max_length=1000)
    star = serializers.BooleanField()
    categories = CategorySerializer(many=True)
    domain = serializers.CharField()
    s3 = serializers.CharField()
    note = serializers.CharField()
    preview = serializers.CharField()
    last_visited = serializers.DateTimeField()
    created = serializers.DateTimeField()


class PageCatPKInfoSerializer(serializers.Serializer):
    pk = serializers.IntegerField(read_only=True)
    title = serializers.CharField(required=True, allow_blank=False)
    url = serializers.CharField(required=True, allow_blank=False, max_length=1000)
    star = serializers.BooleanField()
    cat_pks = serializers.ListField(
            child=serializers.IntegerField()
        )
    domain = serializers.CharField()
    note = serializers.CharField()
    s3 = serializers.CharField()
    preview = serializers.CharField()
    last_visited = serializers.DateTimeField()
    created = serializers.DateTimeField()

class CategoryPageSerializer(serializers.Serializer):
    pk = serializers.IntegerField()
    title = serializers.CharField(max_length=1000)
    pages = PageInfoSerializer(many=True)
    color = serializers.CharField(max_length=7)

class CategoryPagePKSerializer(serializers.Serializer):
    pk = serializers.IntegerField()
    title = serializers.CharField(max_length=1000)
    pages = serializers.ListField(
            child=serializers.IntegerField()
        )
    color = serializers.CharField(max_length=7)

class NewSendCategorySerializer(serializers.Serializer):
    categories = CategoryPagePKSerializer(many=True)
    starred = serializers.ListField(
            child=serializers.IntegerField()
        )
    pages = PageCatPKInfoSerializer(many=True)

class SendCategorySerializer(serializers.Serializer):
    categories = CategoryPageSerializer(many=True)
    starred = PageInfoSerializer(many=True)

class TimeActiveSerializer(serializers.Serializer):
    start = serializers.DateTimeField()
    end = serializers.DateTimeField()

class DomainSerializer(serializers.Serializer):
    pk = serializers.IntegerField()
    base_url = serializers.CharField(max_length=1000)
    created = serializers.DateTimeField()
    closed = serializers.DateTimeField()
    title = serializers.CharField()
    favicon = serializers.CharField()
    active_times = TimeActiveSerializer(many=True)
    pages = serializers.IntegerField()
    opened_from_domain = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    opened_from_tabid = serializers.IntegerField()
    minutes_active = serializers.IntegerField()
    preview = serializers.CharField()

class DomainSerializerRegular(serializers.Serializer):
    pk = serializers.IntegerField()
    base_url = serializers.CharField(max_length=1000)
    created = serializers.DateTimeField()

class TabSerializer(serializers.Serializer):
    domains = DomainSerializer(many=True)
    tab_id = serializers.IntegerField()

class SendTabSerializer(serializers.Serializer):
    tabs = TabSerializer(many=True)

class SessionSerializerNoPVs(serializers.Serializer):
    pk = serializers.IntegerField()
    title = serializers.CharField(max_length=50)
    created = serializers.DateTimeField()
    start = serializers.DateTimeField()
    end = serializers.DateTimeField()
    active = serializers.BooleanField()

class ActiveSessionSerializer(serializers.Serializer):
    active_session = SessionSerializerNoPVs()
    other_sessions = SessionSerializerNoPVs(many=True)

class PageVisitSerializer(serializers.Serializer):
    pk = serializers.IntegerField()
    page = PageSerializer()
    domain = DomainSerializerRegular()
    session = SessionSerializerNoPVs()
    s3 = serializers.CharField()
    html = serializers.CharField()
    visited = serializers.DateTimeField()

class PageVisitSerializerNoHTML(serializers.Serializer):
    pk = serializers.IntegerField()
    page = PageSerializer()
    domain = DomainSerializerRegular()
    session = SessionSerializerNoPVs()
    s3 = serializers.CharField()
    preview = serializers.CharField()
    visited = serializers.DateTimeField()

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
    pagevisits = PageVisitSerializerNoHTML(many=True)

class BlacklistSerializer(serializers.Serializer):
    pk = serializers.IntegerField()
    created = serializers.DateTimeField()
    base_url = serializers.CharField(max_length=1000)

class SessionSerializer(serializers.Serializer):
    pk = serializers.IntegerField()
    created = serializers.DateTimeField()
    title = serializers.CharField(max_length=50)
    start = serializers.DateTimeField()
    end = serializers.DateTimeField()
    active = serializers.BooleanField()
    pagevisits = PageVisitSerializerNoHTML(many=True)

class PopupInfoSerializer(serializers.Serializer):
    categories = CategorySerializer(many=True)
    tracking = serializers.BooleanField()
    page = PageSerializer()
