import datetime

import pytest

from src.app.models import Account, Card, User


@pytest.fixture
def sender_with_bank_requisites(already_verified_user, account_with_owner_and_value, card_with_id_and_corr_account):

    user_model = User.objects.filter(tlg_id=already_verified_user.id).first()
    new_account_model = account_with_owner_and_value(uniq_id=123, owner_user_model=user_model, account_value=0)

    new_account_model.save()
    new_card_model = card_with_id_and_corr_account(uniq_id=1234, corr_account_model=new_account_model)

    new_card_model.save()
    return already_verified_user


@pytest.fixture
def new_user_with_account_and_card(
    user_model_without_verified_pn, card_with_id_and_corr_account, account_with_owner_and_value
):
    async def inner(user_tlg_id, account_uniq_id, card_uniq_id, account_value):
        new_user_model = user_model_without_verified_pn(user_tlg_id)
        await new_user_model.asave()

        new_account_model = account_with_owner_and_value(account_uniq_id, new_user_model, account_value)
        await new_account_model.asave()

        new_card_model = card_with_id_and_corr_account(card_uniq_id, new_account_model)
        await new_card_model.asave()

        return (new_user_model, new_account_model, new_card_model)

    return inner


@pytest.fixture
def new_user_with_account(user_model_without_verified_pn, account_with_owner_and_value):
    async def inner(user_tlg_id, account_uniq_id, account_value):

        new_user_model = user_model_without_verified_pn(user_tlg_id)
        await new_user_model.asave()

        new_account_model = account_with_owner_and_value(account_uniq_id, new_user_model, account_value)
        await new_account_model.asave()

        return (new_user_model, new_account_model)

    return inner


@pytest.fixture
def user_model_without_verified_pn():
    def inner(tlg_id):
        return User(tlg_id=tlg_id, username="testuser", first_name="Still", last_name="Test", phone_number="")

    return inner


@pytest.fixture
def user_model_with_verified_pn():
    def inner(tlg_id):
        return User(
            tlg_id=tlg_id,
            username="testuser",
            first_name="Still",
            last_name="Test",
            phone_number="+542151252",
        )

    return inner


@pytest.fixture
def account_with_owner_and_value():
    def inner(uniq_id, owner_user_model, account_value):
        return Account(uniq_id=uniq_id, owner=owner_user_model, party="PER", currency="USD", value=account_value)

    return inner


@pytest.fixture
def card_with_id_and_corr_account():
    def inner(uniq_id, corr_account_model):
        return Card(uniq_id=uniq_id, corresponding_account=corr_account_model, expiration=datetime.date(2025, 1, 1))

    return inner
