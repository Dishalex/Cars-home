import asyncio

import cloudinary
import cloudinary.uploader

from cloudinary.exceptions import Error as CloudinaryError
from fastapi import HTTPException, UploadFile
from fastapi.responses import JSONResponse
from requests.exceptions import RequestException

from backend.src.conf.config import config

cloudinary.config(
    cloud_name=config.CLD_NAME,
    api_key=config.CLD_API_KEY,
    api_secret=config.CLD_API_SECRET,
)


class CloudService:
    """Class for handling image and file uploads to Cloudinary."""

    @staticmethod
    async def upload_picture(user_id: int, image_file: UploadFile, folder_name: str = None):
        """
        Upload an original image to Cloudinary.

        :param user_id: User ID associated with the image.
        :type user_id: int
        :param image_file: UploadFile object representing the image file.
        :type image_file: UploadFile
        :param folder_name: Optional folder name for organizing images.
        :type folder_name: str
        :return: Tuple containing the URL and public ID of the uploaded image.
        :rtype: tuple
        """
        try:
            if not folder_name:
                folder_name = f"Cars-home/user_{user_id}/original_images"
            response = await asyncio.to_thread(
                cloudinary.uploader.upload,
                image_file.file,
                folder=folder_name,  # type: ignore
            )
            return response['url'], response['public_id']
        except CloudinaryError as e:
            return JSONResponse(status_code=500, content={"message": f"Cloudinary error: {e}"})
            # raise HTTPException(status_code=500, detail=f"Cloudinary error: {e}")
        except RequestException as e:
            return JSONResponse(status_code=500, content={"message": f"Network error: {e}"})
            # raise HTTPException(status_code=500, detail=f"Network error: {e}")
        except Exception as e:
            return JSONResponse(status_code=500, content={"message": f"Uploading image error: {e}"})
            # raise HTTPException(status_code=500, detail=f"Uploading image error: {e}")

    @staticmethod
    async def delete_picture(public_id: str):
        """
        Delete an image from Cloudinary.

        :param public_id: Public ID of the image to be deleted.
        :type public_id: str
        :raises HTTPException: If an error occurs while deleting the image.
        """
        try:
            await asyncio.to_thread(
                cloudinary.uploader.destroy,
                public_id
            )
        except Exception as e:
            return JSONResponse(status_code=500, content={"message": f"Error deleting image: {e}"})
            # raise HTTPException(status_code=500, detail=f"Error deleting image: {e}")

    @staticmethod
    async def update_picture_on_cloudinary(public_id: str, transformation_params: dict):
        """
        Update an image on Cloudinary with specified transformations.

        :param public_id: Public ID of the image to be updated.
        :type public_id: str
        :param transformation_params: Dictionary of transformation parameters.
        :type transformation_params: dict
        :return: URL of the updated image.
        :rtype: str
        """
        try:
            response = await asyncio.to_thread(
                cloudinary.uploader.explicit,
                public_id,
                type='upload',  # type: ignore
                eager=[transformation_params]  # type: ignore
            )

            if 'eager' in response and response['eager']:
                eager_transformed_url = response['eager'][0]['url']
                return eager_transformed_url
        except CloudinaryError as e:
            return JSONResponse(status_code=500, content={"message": f"Cloudinary error: {e}"})
            # raise HTTPException(status_code=500, detail=f"Cloudinary error: {e}")
        except RequestException as e:
            return JSONResponse(status_code=500, content={"message": f"Network error: {e}"})
            # raise HTTPException(status_code=500, detail=f"Network error: {e}")
        except Exception as e:
            return JSONResponse(status_code=500, content={"message": f"Uploading image error: {e}"})
            # raise HTTPException(status_code=500, detail=f"Помилка завантаження зображення: {e}")


cloud_service = CloudService()
