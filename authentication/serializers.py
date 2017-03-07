from django.contrib.auth import update_session_auth_hash

from rest_framework import serializers

from authentication.models import CustomUser
from history.serializers import CategorySerializer


class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    confirm_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'username', 'created_at', 'updated_at',
                  'first_name', 'last_name', 'password',
                  'confirm_password',)
        read_only_fields = ('created_at', 'updated_at',)

        def create(self, validated_data):
            return CustomUser.objects.create(**validated_data)

        def update(self, instance, validated_data):
            instance.username = validated_data.get('username', instance.username)

            instance.save()

            password = validated_data.get('password', None)
            confirm_password = validated_data.get('confirm_password', None)

            if password and confirm_password and password == confirm_password:
                instance.set_password(password)
                instance.save()

            update_session_auth_hash(self.context.get('request'), instance)

            return instance

class UserInfoSerializer(serializers.Serializer):
    pk = serializers.IntegerField()
    email = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    tracking_on = serializers.BooleanField()

class TokenSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=100)

class LoginSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=100)
    key = serializers.CharField()
    md5 = serializers.CharField()
    categories = CategorySerializer(many=True)
