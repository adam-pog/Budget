from django.urls import path

from . import views
from rest_framework.authtoken import views as authtoken_views


urlpatterns = [
    # ex: /auth/...
    path('logout/', views.LogoutView.as_view(), name='index'),
    path('api-token-auth/', authtoken_views.obtain_auth_token),
]
