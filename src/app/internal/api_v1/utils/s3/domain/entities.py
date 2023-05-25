from datetime import datetime

from ninja import Schema


class RemoteImageSchema(Schema):
    uploaded_at: datetime
    content: str
