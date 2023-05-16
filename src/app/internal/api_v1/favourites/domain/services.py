from abc import ABC, abstractmethod
from typing import Any, List

from asgiref.sync import sync_to_async

from app.internal.api_v1.users.domain.entities import UserSchema


class IFavouriteRepository(ABC):
    @abstractmethod
    def get_limited_list_of_favourites(self, tlg_id: int, favs_limit: int) -> List[UserSchema]:
        pass

    @abstractmethod
    def try_del_fav_from_user(self, tlg_id_of_owner: int, fav_user: UserSchema) -> None:
        pass

    @abstractmethod
    def try_add_fav_to_user(self, tlg_id_of_owner: int, new_fav_user: UserSchema) -> None:
        pass

    @abstractmethod
    def get_another_user_by_arg(self, argument: Any) -> UserSchema:
        pass


class FavouriteService:
    def __init__(self, fav_repo: IFavouriteRepository):
        self._fav_repo = fav_repo


    @sync_to_async
    def aget_limited_list_of_favourites(self, tlg_id: int, favs_limit: int) -> List[UserSchema]:
        return self.get_limited_list_of_favourites(tlg_id=tlg_id, favs_limit=favs_limit)
    
    def get_limited_list_of_favourites(self, tlg_id: int, favs_limit: int) -> List[UserSchema]:
        return self._fav_repo.get_limited_list_of_favourites(tlg_id=tlg_id, favs_limit=favs_limit)



    @sync_to_async
    def aget_another_user_by_arg(self, argument: Any) -> UserSchema:
        return self.get_another_user_by_arg(argument=argument)
    
    def get_another_user_by_arg(self, argument: Any) -> UserSchema:
        return self._fav_repo.get_another_user_by_arg(argument=argument)
    


    @sync_to_async
    def atry_del_fav_from_user(self, tlg_id_of_owner: int, fav_user: UserSchema) -> None:
        self.try_del_fav_from_user(tlg_id_of_owner=tlg_id_of_owner, fav_user=fav_user)

    def try_del_fav_from_user(self, tlg_id_of_owner: int, fav_user: UserSchema) -> None:
        self._fav_repo.try_del_fav_from_user(tlg_id_of_owner=tlg_id_of_owner, fav_user=fav_user)



    @sync_to_async
    def atry_add_fav_to_user(self, tlg_id_of_owner: int, new_fav_user: UserSchema) -> None:
        self.try_add_fav_to_user(tlg_id_of_owner=tlg_id_of_owner, new_fav_user=new_fav_user)

    def try_add_fav_to_user(self, tlg_id_of_owner: int, new_fav_user: UserSchema) -> None:
        self._fav_repo.try_add_fav_to_user(tlg_id_of_owner=tlg_id_of_owner, new_fav_user=new_fav_user)
