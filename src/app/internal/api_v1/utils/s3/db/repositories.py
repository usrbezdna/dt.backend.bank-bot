
from app.internal.api_v1.utils.s3.domain.services import IS3Repository
from app.internal.api_v1.utils.s3.db.models import RemoteImage

from django.core.files.images import ImageFile

from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings

class YandexCloudStorage(S3Boto3Storage):
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    location = 'telegram'

    default_acl = 'public-read'
    file_overwrite = True


class S3Repository(IS3Repository):

    async def save_image_to_s3_bucket(self, image : ImageFile):
        """
        Saves image file to object storage.
        """
        await RemoteImage.objects.acreate(content=image)
