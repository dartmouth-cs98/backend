from rest_framework import serializers
from history.models import Category, Page
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    pages = serializers.PrimaryKeyRelatedField(many=True, queryset=Page.objects.all())
    categories = serializers.PrimaryKeyRelatedField(many=True, queryset=Category.objects.all())

    class Meta:
        model = User
        fields = ('id', 'username', 'pages', 'categories')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'title', 'created', 'owner')
    owner = serializers.ReadOnlyField(source='owner.username')


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
    # class Meta:
    #     model = Page
    #     fields = ('id', 'title', 'url', 'star', 'categories', 'created', 'owner')
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(required=True, allow_blank=False, max_length=100)
    url = serializers.CharField(required=True, allow_blank=False, max_length=1000)
    star = serializers.BooleanField()
    categories = CategorySerializer(many=True)
    created = serializers.DateTimeField()
    owner = serializers.ReadOnlyField(source='owner.username')

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
