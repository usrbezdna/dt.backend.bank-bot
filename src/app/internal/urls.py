from django.urls import path

from .api import global_ninja_api

# API Calls Go Here
urlpatterns = [
    path("", global_ninja_api.urls),
]
