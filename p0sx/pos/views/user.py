from pos.models.user import User

from pos.serializers.user import CrewSerializer

from rest_framework import viewsets


# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = CrewSerializer
    filter_fields = ('card',)
