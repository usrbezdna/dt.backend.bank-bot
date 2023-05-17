
from io import BytesIO
from abc import ABC, abstractmethod
from asgiref.sync import sync_to_async

from telegram import Update
from telegram.ext import ContextTypes
from django.core.files.images import ImageFile



class IS3Repository(ABC):

    @abstractmethod
    async def save_image_to_s3_bucket(self, image : ImageFile):
        pass

class S3Service():

    def __init__(self, s3_repo : IS3Repository):
        self._s3_repo = s3_repo


    async def asave_telegram_photo_to_bucket(self, update : Update, context : ContextTypes.DEFAULT_TYPE) -> ImageFile:
        """
        Recieves Telegram Update object, extracts photo 
        and sends it to internal repo for saving to object storage  
        """

        photo_id = update.message.photo[-1].file_id
        photo_file = await context.bot.get_file(photo_id)

        memory_file = BytesIO()
        await photo_file.download_to_memory(memory_file)

        image = ImageFile(BytesIO(memory_file.getvalue()), name=f'{photo_id}.jpg')

        await self._s3_repo.save_image_to_s3_bucket(image=image)
        return image


    # async def get_pre_signed_url(self, )


