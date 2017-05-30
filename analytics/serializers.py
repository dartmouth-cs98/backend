from rest_framework import serializers

class PageSerializer(serializers.Serializer):
    title = serializers.CharField()
    url = serializers.CharField()

class PagesSerializer(serializers.Serializer):
    day = PageSerializer(many=True)
    week = PageSerializer(many=True)
    month = PageSerializer(many=True)

class DomainSerializer(serializers.Serializer):
    name = serializers.CharField()
    value = serializers.IntegerField()

class DomainsSerializer(serializers.Serializer):
    day = DomainSerializer(many=True)
    week = DomainSerializer(many=True)
    month = DomainSerializer(many=True)

class PVFloatSerializer(serializers.Serializer):
    datetime = serializers.CharField()
    pages = serializers.FloatField()
    pagevisits = serializers.FloatField()

class PVSerializer(serializers.Serializer):
    datetime = serializers.CharField()
    pages = serializers.IntegerField()
    pagevisits = serializers.IntegerField()

class WeeksPVSerializer(serializers.Serializer):
    current = PVSerializer(many=True)
    last = PVSerializer(many=True)
    average = PVFloatSerializer(many=True)

class PageVisitsSerializer(serializers.Serializer):
    day = PVSerializer(many=True)
    week = WeeksPVSerializer()
    month = PVSerializer(many=True)

class ProductivitySerializer(serializers.Serializer):
    procrastination_sites = serializers.ListField(child=serializers.CharField())
    visits = DomainsSerializer()
    minutes = DomainsSerializer()

class ProcrastinationSitesSerializer(serializers.Serializer):
    procrastination_sites = serializers.ListField(child=serializers.CharField())

class AnalyticsSerializer(serializers.Serializer):
    page_visits = PageVisitsSerializer()
    user_domains = DomainsSerializer()
    hindsite_domains = DomainsSerializer()
    user_pages = PagesSerializer()
    productivity = ProductivitySerializer()
