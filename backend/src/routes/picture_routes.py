import asynctempfile
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from DS.funcs_repo.image_process_async import plate_recognize
from backend.src.database.db import get_db
from backend.src.entity.models import User
from backend.src.repository.history import create_entry, create_exit
from backend.src.repository.picture import create_picture
from backend.src.routes.notification import telegram_notification
from backend.src.services.auth import auth_service
from backend.src.services.cloudstore import cloud_service

router = APIRouter(prefix="/parking", tags=["parking"])


@router.post("/entry")
async def park_entry(
        user: User = Depends(auth_service.get_current_user),
        photo: UploadFile = File(...),
        plate_number: str = Form(None),
        session: AsyncSession = Depends(get_db)
) -> dict:
    try:
        
        async with asynctempfile.NamedTemporaryFile(delete=False) as temp_file:
            await temp_file.write(await photo.read())
            file_path = temp_file.name

        img_processed, recognized_symbols = await plate_recognize(file_path)        

        if not recognized_symbols and not plate_number:
            raise HTTPException(status_code=400, detail="Номерний знак не розпізнано і не введено вручну")
        
        img_url, cloudinary_public_id = await cloud_service.upload_picture(img_processed, 'Entry_photos')
        
        picture = await create_picture(session, recognized_symbols or plate_number, img_url, cloudinary_public_id)

        history = await create_entry(recognized_symbols or plate_number, picture.id, session)  # Виклик функції create_entry
        await telegram_notification("in", user)
        return {"message": "Welcome to Cars Home!", "image_url": img_url, "plate_number": recognized_symbols or plate_number}
    #TODO create scheme
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/exit")
async def park_exit(
        user: User = Depends(auth_service.get_current_user),
        photo: UploadFile = File(...),
        plate_number: str = Form(None),
        session: AsyncSession = Depends(get_db)
) -> dict:

    try:
        async with asynctempfile.NamedTemporaryFile(delete=False) as temp_file:
            await temp_file.write(await photo.read())
            file_path = temp_file.name

        img_processed, recognized_symbols = await plate_recognize(file_path)        

        if not recognized_symbols and not plate_number:
            raise HTTPException(status_code=400, detail="Номерний знак не розпізнано і не введено вручну")
        
        img_url, cloudinary_public_id = await cloud_service.upload_picture(img_processed, 'Exit_photos')
        
        picture = await create_picture(session, recognized_symbols or plate_number, img_url, cloudinary_public_id)

        history = await create_exit(recognized_symbols or plate_number, picture.id, session)
        await telegram_notification("out", user)
        return {"message": "Have a good trip!", "image_url": img_url, "plate_number": recognized_symbols or plate_number}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
