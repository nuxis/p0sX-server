from pos.models.user import User, UserSession

from rest_framework import serializers


class CrewSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'credit', 'card', 'is_cashier')


class CrewSessionSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserSession
        fields = ('user', 'django_user')
