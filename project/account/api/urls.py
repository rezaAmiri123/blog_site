from django.urls import path
from . import views


urlpatterns = [
    path('delete/', views.TestUserDelete.as_view(), name='user_delete'),
]

