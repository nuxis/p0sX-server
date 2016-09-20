from pos.models.crew import Crew

from rest_framework import serializers


class CrewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Crew
        fields = ('first_name', 'last_name', 'credit', 'card')
