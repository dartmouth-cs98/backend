from rest_framework import serializers
from history.models import Category, Page


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'title', 'created')

    def create(self, validated_data):
        """
        Create and return a new `Category` instance, given the validated data.
        """
        return Category.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Category` instance, given the validated data.
        """
        instance.title = validated_data.get('title', instance.title)
        instance.save()
        return instance

class PageSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(required=True, allow_blank=False, max_length=100)
    url = serializers.CharField(required=True, allow_blank=False, max_length=1000)
    star = serializers.BooleanField()
    categories = CategorySerializer(many=True)
    created = serializers.DateTimeField()

    def create(self, validated_data):
        """
        Create and return a new `Category` instance, given the validated data.
        """
        return Page.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Category` instance, given the validated data.
        """
        instance.title = validated_data.get('title', instance.title)
        instance.url = validated_data.get('url', instance.url)
        instance.star = validated_data.get('star', instance.star)
        instance.save()
        return instance
