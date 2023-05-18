
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

    async def get_image_from_s3_bucket(self, image_id : int):
        """
        Returns image from object storage.
        """
        return await RemoteImage.objects.aget(pk=image_id)
    
    async def get_presigned_url_for_image(self, image_id : int):
        """
        Returns presigned_url for image
        """
        image = await RemoteImage.objects.aget(pk=image_id)

        presigned_url = image.content.storage.bucket.meta.client.\
            generate_presigned_url(
            'get_object', 
            Params={
                'Bucket': f'{settings.AWS_STORAGE_BUCKET_NAME}', 
                "Key": f"telegram/{image.content.name}"
            }
        )

        return presigned_url