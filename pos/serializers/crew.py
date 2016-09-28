from pos.models.crew import Crew, CrewSession

from rest_framework import serializers


class CrewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Crew
        fields = ('first_name', 'last_name', 'credit', 'card')


class CrewSessionSerializer(serializers.ModelSerializer):

    class Meta:
        model = CrewSession
        fields = ('crew', 'user')
