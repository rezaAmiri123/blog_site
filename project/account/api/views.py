from rest_framework import generics
from django.contrib.auth import get_user_model
from .serializers import TestUserSerializer

User = get_user_model()


class TestUserDelete(generics.DestroyAPIView):
    queryset = User.objects.all
    serializer_class = TestUserSerializer
