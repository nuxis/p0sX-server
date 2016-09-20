from pos.models.crew import Crew

from pos.serializers.crew import CrewSerializer

from rest_framework import viewsets


# ViewSets define the view behavior.
class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    filter_fields = ('card',)
