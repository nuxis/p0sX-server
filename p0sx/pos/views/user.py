from pos.models.user import User
from pos.serializers.user import CrewSerializer
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response


# ViewSets define the view behavior.
class UserViewSet(viewsets.ViewSet):

    def retrieve(self, request, pk=None):
        users = User.objects.all()
        user = get_object_or_404(users, card__iexact=pk)
        serializer = CrewSerializer(user)
        return Response(serializer.data)
