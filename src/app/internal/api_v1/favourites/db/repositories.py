import logging
from typing import Any, List, Optional

from app.internal.api_v1.favourites.db.exceptions import (
    FavouriteNotFoundException,
    InvalidIDArgumentException,
    SecondTimeAdditionException,
    UserNotInFavouritesException,
)
from app.internal.api_v1.favourites.db.models import Favourite
from app.internal.api_v1.favourites.domain.services import IFavouriteRepository
from app.internal.api_v1.users.db.exceptions import UserNotFoundException
from app.internal.api_v1.users.db.models import User
from app.internal.api_v1.users.db.repositories import UserRepository
from app.internal.api_v1.users.domain.entities import UserSchema

logger = logging.getLogger("django_stdout")


class FavouriteRepository(IFavouriteRepository):
    def __init__(self, user_repo: UserRepository) -> None:
        self._user_repo = user_repo

    def get_limited_list_of_favourites(self, tlg_id: int, favs_limit: int) -> List[UserSchema]:
        """
        Returns limited list of favourite users for Telegram User
        with ID tlg_id or raises FavouriteNotFoundException (if fav_obj was not found)
        ----------

        :param tlg_id: Telegram ID of this user
        :param favs_limit: limit of favs in result list
        """
        fav_opt: Optional[Favourite] = Favourite.objects.filter(tlg_id=tlg_id).first()

        if fav_opt is None:
            raise FavouriteNotFoundException("There is no Favourite object with such owner")

        return [UserSchema.from_orm(user_model) for user_model in fav_opt.favourites.all()[:favs_limit]]

    def try_del_fav_from_user(self, tlg_id_of_owner: int, fav_user: UserSchema) -> None:
        """
        Deletes fav_user from the list of favourites of user with ID tlg_id_of_owner
        or raises UserNotInFavouritesException
        ----------

        :param tlg_id_of_owner: Telegram ID of list owner
        :param fav_user: user that will be deleted from favourites
        :raises UserNotInFavouritesException: if fav_user actually
        """

        favs_manager = Favourite.objects.get(tlg_id=tlg_id_of_owner).favourites

        if favs_manager.filter(pk=fav_user.tlg_id).exists():
            user_model = User.objects.get(pk=fav_user.tlg_id)
            favs_manager.remove(user_model)

            logger.info(f"User with ID {fav_user.tlg_id} was deleted from favourites of user {tlg_id_of_owner}")
            return

        raise UserNotInFavouritesException()

    def try_add_fav_to_user(self, tlg_id_of_owner: int, new_fav_user: UserSchema) -> None:
        """
        Tries to add new User object to the list of favourites
        for another Telegram User (tlg_id_of_owner).
        Raises SecondTimeAdditionException if new_fav_user have already been in favs
        ----------

        :param tlg_id_of_owner: Telegram ID of list owner
        :param new_fav_user: new favourite User obj

        """

        favs_manager = Favourite.objects.get_or_create(tlg_id=tlg_id_of_owner)[0].favourites

        if not favs_manager.filter(pk=new_fav_user.tlg_id).exists():
            user_model = User.objects.get(pk=new_fav_user.tlg_id)
            favs_manager.add(user_model)

            logger.info(f"User with ID {new_fav_user.tlg_id} added as favourite for {tlg_id_of_owner}")
            return

        raise SecondTimeAdditionException()

    def get_another_user_by_arg(self, argument: Any) -> UserSchema:
        """
        This function tries to get user by username or Telegram ID.
        Returns User object or raises InvalidIDArgumentException | UserNotFoundException
        ----------

        :param argument: argument of /add_fav command
        :return: if user was found, then User object is returned
        :raises InvalidIDArgumentException | UserNotFoundException:
        """

        if argument.startswith("@"):
            another_user: UserSchema = self._user_repo.get_user_by_username(argument[1:])

        elif not argument.isdigit() or int(argument) <= 0:
            raise InvalidIDArgumentException()

        else:
            another_user: UserSchema = self._user_repo.get_user_by_id(argument)

        return another_user
