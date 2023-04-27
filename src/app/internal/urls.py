from django.urls import path

from .transport.rest.api import ninja_api

# API Calls Go Here
urlpatterns = [
    path("", ninja_api.urls),
]
