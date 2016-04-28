from pos.models.simplelog import Log

from rest_framework import serializers


class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = ('when', 'what', 'who')
