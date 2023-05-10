from ninja import NinjaAPI
from ninja_extra import NinjaExtraAPI
from ninja_jwt.controller import NinjaJWTDefaultController


from app.internal.api_v1.users.api import register_users_api


def create_global_api() -> NinjaExtraAPI:
    """
    Creates NinjaAPI with routers
    :return: Global API
    """

    global_api = NinjaExtraAPI(
        title="NinjaREST",
        description="REST API",
        version="1.0.0",
    )

    global_api.register_controllers(NinjaJWTDefaultController)

    register_users_api(global_api)
    return global_api


global_ninja_api = create_global_api()
