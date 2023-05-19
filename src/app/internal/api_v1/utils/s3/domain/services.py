
from io import BytesIO
from abc import ABC, abstractmethod
from asgiref.sync import sync_to_async

from telegram import Update
from telegram.ext import ContextTypes
from django.core.files.images import ImageFile



class IS3Repository(ABC):

    @abstractmethod
    async def get_image_from_s3_bucket(self, image_id : int):
        pass

    @abstractmethod
    async def get_presigned_url_for_image(self, image_id : int):
        pass

class S3Service():

    def __init__(self, s3_repo : IS3Repository):
        self._s3_repo = s3_repo


    async def aconvert_telegram_photo_to_image(self, update : Update, context : ContextTypes.DEFAULT_TYPE) -> ImageFile:
        """
        Recieves Telegram Update object, extracts photo and creates ImageFile 
        """

        photo_id = update.message.photo[-1].file_id
        photo_file = await context.bot.get_file(photo_id)

        memory_file = BytesIO()
        await photo_file.download_to_memory(memory_file)

        image_name = f'{photo_id}.jpg'
        image_file = ImageFile(BytesIO(memory_file.getvalue()), name=image_name)

        return image_file


    async def aget_presigned_url_for_image(self, image_id : int):
        return await self._s3_repo.get_presigned_url_for_image(image_id=image_id)
    
    async def aget_image_from_s3_bucket(self, image_id : int):
        return await self._s3_repo.get_image_from_s3_bucket(image_id=image_id)




