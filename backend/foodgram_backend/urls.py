from django.contrib import admin
from django.urls import include, path

from recipes.views import redirect_short_link

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('users.urls')),
    path('api/', include('recipes.urls')),
    path('s/<str:link>/', redirect_short_link, name='recipe-redirect')
]
