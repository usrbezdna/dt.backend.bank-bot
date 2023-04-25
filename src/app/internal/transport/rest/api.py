from ninja import NinjaAPI
from app.internal.transport.rest.routers import me_router

from ninja_jwt.controller import NinjaJWTDefaultController
from ninja_extra import NinjaExtraAPI

def create_api():
    """
    Creates NinjaAPI with routers
    :return: api
    """

    api = NinjaExtraAPI(
        title='NinjaREST',
        description='REST API',
        version='1.0.0',
    )

    api.register_controllers(NinjaJWTDefaultController)
    add_routers(api)
    
    return api


def add_routers(api : NinjaAPI):
    """
    Attaches routers to Ninja API obj
    """
    api.add_router('/me', me_router)


ninja_api = create_api()