import json
import pytest

from django.test import Client

from src.app.internal.api_v1.users.domain.entities import UserSchema
from src.app.internal.api_v1.users.presentation.rest.content_messages import (
    INVALID_PHONE_NUMBER, NOT_VERIFIED, PASSWORD_SUCCESS, PHONE_NUMBER_SUCCESS
)

from src.app.models import User

@pytest.mark.rest
@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
@pytest.mark.error_case
async def test_me_endpoint_without_verified_pn(
    get_access_token_for_user,
    already_saved_user, async_client
):
    access_token = await get_access_token_for_user(already_saved_user)
    me_response = await async_client.get(
        path='/api/users/me', headers={'Authorization': f'Bearer {access_token}'}
    )

    assert me_response.status_code == 403
    assert me_response.json()['message'] == NOT_VERIFIED



@pytest.mark.rest
@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
@pytest.mark.valid_case
async def test_me_endpoint_with_valid(
    get_access_token_for_user,
    already_verified_user, async_client
):
    access_token = await get_access_token_for_user(already_verified_user)

    me_response = await async_client.get(
        path='/api/users/me', headers={'Authorization': f'Bearer {access_token}'}
    )

    user_model = await User.objects.aget(pk=already_verified_user.id)

    assert me_response.status_code == 200
    assert UserSchema.from_orm(user_model) == me_response.json()



@pytest.mark.rest
@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
@pytest.mark.error_case
async def test_phone_endpoint_with_unparsed_pn(
    get_access_token_for_user,
    already_verified_user, async_client
):
    access_token = await get_access_token_for_user(already_verified_user)

    query_param = 'new_phone=%2Babcdedgt5'
    phone_response = await async_client.post(
        path=f'/api/users/phone?{query_param}', headers={'Authorization': f'Bearer {access_token}'}
    )

    assert phone_response.status_code == 400
    assert phone_response.json()['message'] == INVALID_PHONE_NUMBER



@pytest.mark.rest
@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
@pytest.mark.error_case
async def test_phone_endpoint_with_invalid_pn(
    get_access_token_for_user,
    already_verified_user, async_client
):
    access_token = await get_access_token_for_user(already_verified_user)

    query_param = 'new_phone=%2B5215125'
    phone_response = await async_client.post(
        path=f'/api/users/phone?{query_param}', headers={'Authorization': f'Bearer {access_token}'}
    )

    assert phone_response.status_code == 400
    assert phone_response.json()['message'] == INVALID_PHONE_NUMBER




@pytest.mark.rest
@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
@pytest.mark.valid_case
async def test_phone_endpoint_with_valid_pn(
    get_access_token_for_user,
    already_verified_user, async_client
):
    access_token = await get_access_token_for_user(already_verified_user)

    query_param = 'new_phone=%2B79267378397'
    phone_response = await async_client.post(
        path=f'/api/users/phone?{query_param}', headers={'Authorization': f'Bearer {access_token}'}
    )

    assert phone_response.status_code == 200
    assert phone_response.json()['message'] == PHONE_NUMBER_SUCCESS

    assert await User.objects.values_list('phone_number', flat=True).aget(pk=already_verified_user.id) == '+79267378397'


@pytest.mark.rest
@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
@pytest.mark.valid_case
async def test_password_endpoint_valid(
    get_access_token_for_user,
    already_verified_user, async_client
):
    access_token = await get_access_token_for_user(already_verified_user)

    old_password = await User.objects.values_list('password', flat=True).aget(pk=already_verified_user.id)

    query_param = 'new_password=9763164741464574'
    password_response = await async_client.post(
        path=f'/api/users/password?{query_param}', headers={'Authorization': f'Bearer {access_token}'}
    )

    updated_password = await User.objects.values_list('password', flat=True).aget(pk=already_verified_user.id)
    
    assert password_response.status_code == 200
    assert password_response.json()['message'] == PASSWORD_SUCCESS

    assert old_password != updated_password

    
