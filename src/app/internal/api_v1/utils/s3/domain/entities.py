from ninja import Schema

from datetime import datetime


class RemoteImageSchema(Schema):
    uploaded_at : datetime
    content : str