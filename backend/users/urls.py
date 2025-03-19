from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import CustomAuthToken, CustomTokenLogout, CustomUserViewSet

v1_router = DefaultRouter()
v1_router.register('users', CustomUserViewSet, basename='users')

urlpatterns = [
    path('', include(v1_router.urls)),
    path('auth/token/login/', CustomAuthToken.as_view(), name='login'),
    path('auth/token/logout/', CustomTokenLogout.as_view(), name='logout'),
]
