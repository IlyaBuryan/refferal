from django.urls import path
from .views import auth_user, check_code, UserUpdateView, user_view

urlpatterns = [
    path('user_auth/', auth_user, name='user_auth'),
    path('check_code/', check_code, name='check_code'),

    path('user_view/<int:user_pk>/', user_view, name='user_view'),
    path('user_update/<int:pk>/', UserUpdateView.as_view(), name='user_update'),
]
