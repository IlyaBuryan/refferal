from rest_framework import serializers
from .models import User, UserLogin


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('phone',)


class UserLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLogin
        fields = ('phone',)


class UserRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'phone', 'self_invite_code', 'other_invite_code')


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'other_invite_code')
