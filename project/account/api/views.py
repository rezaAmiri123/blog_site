from rest_framework import generics, permissions
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import RegisterUserSerializer, UserListSerializer, UserDetailSerializer
from .permissions import IsOwner
from account.models import Contact
from actions.utils import create_action

User = get_user_model()


class RegisterUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterUserSerializer


class ListUserView(generics.ListAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserListSerializer


class UserRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.IsAuthenticated, IsOwner)
    serializer_class = UserDetailSerializer


class UserFollowView(generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        user_id = request.data.get('id')
        action = request.data.get('action')
        if user_id and action:
            try:
                user = User.objects.get(id=user_id)
                if action == 'follow':
                    Contact.objects.get_or_create(user_from=request.user,
                                                  user_to=user)
                    create_action(request.user, 'is following', user)
                else:
                    Contact.objects.filter(user_from=request.user,
                                           user_to=user).delete()
                    create_action(request.user, 'is unfollowing', user)
                return Response({'status': 'ok'})
            except User.DoesNotExist:
                return Response({'status': 'ko'})
        return Response({'status': 'ko'})


