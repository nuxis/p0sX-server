from pos.models.crew import Crew

from rest_framework import serializers


class CrewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Crew
        fields = ('name', 'max_credit', 'card')
