from django.urls import path

from .transport.rest.handlers import WebAPIView

# API Calls Go Here
urlpatterns = [
    path("me/<int:tlg_id>/", WebAPIView.as_view(), name="web_api"),
]
