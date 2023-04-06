import pytest
from django.urls import reverse


@pytest.fixture
def web_api_url():
    def inner_with_tlg_id(tlg_id):
        return reverse("web_api", args=[tlg_id])

    return inner_with_tlg_id
