from ninja.orm import create_schema
from app.internal.api_v1.favourites.db.models import Favourite


FavouriteSchema = create_schema(
    Favourite,
    depth=1
)

class FavouriteOut(FavouriteSchema):
    pass

class FavouriteIn(FavouriteSchema):
    pass
