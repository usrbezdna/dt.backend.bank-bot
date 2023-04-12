import pytest
from rest_framework import status

from src.app.internal.transport.rest import content_messages
from src.app.internal.transport.rest.serializers import TelegramUserSerializer
from src.app.models import User


@pytest.mark.unit
@pytest.mark.django_db
def test_absent_user(client, web_api_url):
    """
    Test case with User absent in DB
    """
    url_for_user = web_api_url(tlg_id=1337)
    resp = client.get(url_for_user)

    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert resp.data == content_messages.USER_NOT_FOUND


@pytest.mark.unit
@pytest.mark.django_db(transaction=True)
def test_user_without_verified_phone(client, web_api_url, user_model_without_verified_pn):
    """
    Test case with User without the verified phone number
    """

    resticted_user = user_model_without_verified_pn(tlg_id=123)
    resticted_user.save()

    url_for_user = web_api_url(tlg_id=123)
    resp = client.get(url_for_user)

    assert resp.status_code == status.HTTP_403_FORBIDDEN
    assert resp.data == content_messages.NO_PHONE_VERIFICATION


@pytest.mark.unit
@pytest.mark.django_db(transaction=True)
def test_user_with_verified_phone(client, web_api_url, user_model_with_verified_pn):
    """
    Test case with User with verified phone number
    """

    verified_user = user_model_with_verified_pn(tlg_id=123)
    verified_user.save()

    url_for_user = web_api_url(tlg_id=123)
    resp = client.get(url_for_user)

    assert resp.status_code == status.HTTP_200_OK
    assert resp.data == TelegramUserSerializer(verified_user).data
