import pytest 

from src.app.internal.api_v1.favourites.presentation.rest.content_messages import (
    ADDED_SUCCESS, DELETED_SUCCESS, FAVS_NOT_FOUND, FAV_USER_NOT_FOUND, NO_SECOND_TIME_ADDITION, 
    NOT_IN_FAV, SELF_OPS_PROHIBITED
)
from src.app.internal.api_v1.users.domain.entities import UserSchema

from src.app.models import Favourite

@pytest.mark.rest
@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
@pytest.mark.error_case
async def test_list_favourites_endpoint_with_no_favs(
    get_access_token_for_user,
    already_verified_user, async_client
):

    access_token = await get_access_token_for_user(already_verified_user)

    fav_response = await async_client.get(
        path=f'/api/favourites', headers={'Authorization': f'Bearer {access_token}'}
    )

    assert fav_response.status_code == 404
    assert fav_response.json()['message'] == FAVS_NOT_FOUND


@pytest.mark.rest
@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
@pytest.mark.error_case
async def test_list_favourites_endpoint_with_empty_favs(
    get_access_token_for_user,
    already_verified_user, async_client
):

    access_token = await get_access_token_for_user(already_verified_user)
    await Favourite.objects.acreate(tlg_id=already_verified_user.id)

    fav_response = await async_client.get(
        path=f'/api/favourites', headers={'Authorization': f'Bearer {access_token}'}
    )

    assert fav_response.status_code == 404
    assert fav_response.json()['message'] == FAVS_NOT_FOUND


@pytest.mark.rest
@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
@pytest.mark.valid_case
async def test_list_favourites_endpoint_valid(
    user_model_with_id_and_username,
    get_access_token_for_user,
    already_verified_user, 
    async_client,
):
    access_token = await get_access_token_for_user(already_verified_user)

    first_fav = user_model_with_id_and_username(tlg_id=777, username='One')
    await first_fav.asave()

    second_fav = user_model_with_id_and_username(tlg_id=888, username='Two')
    await second_fav.asave()

    fav_obj = Favourite(tlg_id=already_verified_user.id)
    await fav_obj.asave()

    await fav_obj.favourites.aadd(first_fav)
    await fav_obj.favourites.aadd(second_fav)


    fav_response = await async_client.get(
        path=f'/api/favourites', headers={'Authorization': f'Bearer {access_token}'}
    )

    assert fav_response.status_code == 200
    assert fav_response.json() == [UserSchema.from_orm(i) for i in [first_fav, second_fav]]



@pytest.mark.rest
@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
@pytest.mark.error_case
async def test_add_and_del_favourites_endpoint_with_db_miss(
    get_access_token_for_user,
    already_verified_user, 
    async_client,
):
    access_token = await get_access_token_for_user(already_verified_user)

    add_query = 'tlg_id=626236326' 
    add_response = await async_client.put(
        path=f'/api/favourites?{add_query}', headers={'Authorization': f'Bearer {access_token}'}
    )

    del_query = 'tlg_id=36361253151'
    del_response = await async_client.delete(
        path=f'/api/favourites?{del_query}', headers={'Authorization': f'Bearer {access_token}'}
    )

    assert add_response.status_code == 404
    assert add_response.json()['message'] == FAV_USER_NOT_FOUND

    assert del_response.status_code == 404
    assert del_response.json()['message'] == FAV_USER_NOT_FOUND


@pytest.mark.rest
@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
@pytest.mark.error_case
async def test_add_and_del_favourites_endpoint_with_ops_restiction(
    get_access_token_for_user,
    already_verified_user, 
    async_client,
):

    access_token = await get_access_token_for_user(already_verified_user)

    add_query = f'tlg_id={already_verified_user.id}' 
    add_response = await async_client.put(
        path=f'/api/favourites?{add_query}', headers={'Authorization': f'Bearer {access_token}'}
    )

    del_query = f'tlg_id={already_verified_user.id}'
    del_response = await async_client.delete(
        path=f'/api/favourites?{del_query}', headers={'Authorization': f'Bearer {access_token}'}
    )

    
    assert add_response.status_code == 403
    assert add_response.json()['message'] == SELF_OPS_PROHIBITED

    assert del_response.status_code == 403
    assert del_response.json()['message'] == SELF_OPS_PROHIBITED


@pytest.mark.rest
@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
@pytest.mark.error_case
async def test_add_favourites_endpoint_with_second_addition(
    user_model_with_id_and_username,
    get_access_token_for_user,
    already_verified_user, 
    async_client,
):
    new_fav = user_model_with_id_and_username(tlg_id=777, username='One')
    await new_fav.asave()

    fav_obj = Favourite(tlg_id=already_verified_user.id)
    await fav_obj.asave()

    await fav_obj.favourites.aadd(new_fav)

    access_token = await get_access_token_for_user(already_verified_user)

    add_query = f'tlg_id={new_fav.tlg_id}' 
    add_response = await async_client.put(
        path=f'/api/favourites?{add_query}', headers={'Authorization': f'Bearer {access_token}'}
    )

    add_response.status_code == 403
    add_response.json()['message'] == NO_SECOND_TIME_ADDITION


@pytest.mark.rest
@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
@pytest.mark.valid_case
async def test_add_favourites_endpoint_valid(
    user_model_with_id_and_username,
    get_access_token_for_user,
    already_verified_user, 
    async_client,
):
    access_token = await get_access_token_for_user(already_verified_user)

    new_fav = user_model_with_id_and_username(tlg_id=777, username='One')
    await new_fav.asave()

    add_query = f'tlg_id={new_fav.tlg_id}' 
    add_response = await async_client.put(
        path=f'/api/favourites?{add_query}', headers={'Authorization': f'Bearer {access_token}'}
    )

    add_response.status_code == 200
    add_response.json()['message'] == ADDED_SUCCESS

    fav_obj = await Favourite.objects.aget(pk=already_verified_user.id)
    assert await fav_obj.favourites.acontains(new_fav)



@pytest.mark.rest
@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
@pytest.mark.error_case
async def test_del_favourites_endpoint_with_user_not_in_fav(
    user_model_with_id_and_username,
    get_access_token_for_user,
    already_verified_user, 
    async_client,
):
    
    new_fav = user_model_with_id_and_username(tlg_id=777, username='One')
    await new_fav.asave()

    fav_obj = Favourite(tlg_id=already_verified_user.id)
    await fav_obj.asave()

    access_token = await get_access_token_for_user(already_verified_user)

    del_query = f'tlg_id={new_fav.tlg_id}'
    del_response = await async_client.delete(
        path=f'/api/favourites?{del_query}', headers={'Authorization': f'Bearer {access_token}'}
    )

    del_response.status_code == 403
    del_response.json()['message'] == NOT_IN_FAV


@pytest.mark.rest
@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
@pytest.mark.valid_case
async def test_del_favourites_endpoint_valid(
    user_model_with_id_and_username,
    get_access_token_for_user,
    already_verified_user, 
    async_client,
):
    new_fav = user_model_with_id_and_username(tlg_id=777, username='One')
    await new_fav.asave()

    fav_obj = Favourite(tlg_id=already_verified_user.id)

    await fav_obj.asave()
    await fav_obj.favourites.aadd(new_fav)

    access_token = await get_access_token_for_user(already_verified_user)

    del_query = f'tlg_id={new_fav.tlg_id}'
    del_response = await async_client.delete(
        path=f'/api/favourites?{del_query}', headers={'Authorization': f'Bearer {access_token}'}
    )

    del_response.status_code == 200
    del_response.json()['message'] == DELETED_SUCCESS

    fav_obj = await Favourite.objects.aget(pk=already_verified_user.id)
    assert await fav_obj.favourites.acontains(new_fav) is False


