import pytest
import json

from src.app.models import User
from django.test import Client, AsyncClient



@pytest.fixture(scope='session')
def get_access_token_for_user(async_client):
    async def inner(some_user):
        user_model = await User.objects.aget(tlg_id=some_user.id)
        
        user_model.set_password('123456')
        await user_model.asave()

        req_data = {"password": '123456', "tlg_id": some_user.id }
        token_response = await async_client.post(
            path='/api/token/pair', data=json.dumps(req_data), content_type='application/json',
        )

        access_token = token_response.json()['access']
        return access_token
    
    return inner


@pytest.fixture(scope='session')
def async_client():
    client = AsyncClient()
    return client


@pytest.fixture
def user_model_with_id_and_username():
    def inner(tlg_id, username):
        return User(
            tlg_id=tlg_id, 
            username=username, 
            first_name="Still", 
            last_name="Test", 
            phone_number=""
        )

    return inner