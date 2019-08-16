from django.urls import path
from . import views


urlpatterns = [
    path('register/', views.RegisterUserView.as_view(), name='api_register_user'),
    path('users/', views.ListUserView.as_view(), name='api_list_user'),
    path('users/<int:pk>/',
         views.UserRetrieveUpdateView.as_view(),
         name='api_retrieve_update_user'),
    path('user/follow/', views.UserFollowView.as_view(), name='api_user_follow'),
]


