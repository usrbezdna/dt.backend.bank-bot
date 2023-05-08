from ninja import NinjaAPI
from ninja_extra import NinjaExtraAPI
from ninja_jwt.controller import NinjaJWTDefaultController

from app.internal.transport.rest.routers import me_router


def create_api() -> NinjaExtraAPI:
    """
    Creates NinjaAPI with routers
    :return: api
    """

    api = NinjaExtraAPI(
        title="NinjaREST",
        description="REST API",
        version="1.0.0",
    )

    api.register_controllers(NinjaJWTDefaultController)

    add_routers(api)
    return api


def add_routers(api: NinjaExtraAPI):
    """
    Attaches routers to Ninja API obj
    """
    api.add_router("/me", me_router)


ninja_api = create_api()