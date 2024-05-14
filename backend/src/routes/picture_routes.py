from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.database.db import get_db
from backend.src.schemas.history_schema import HistoryUpdate
from backend.src.services.cloudstore import cloud_service
from backend.src.repository.picture import create_picture
from DS.funcs_repo.image_process_async import plate_recognize
from backend.src.repository.history import create_entry, create_exit
from backend.src.entity.models import History
from backend.src.services.auth import auth_service

import asynctempfile

router = APIRouter(prefix="/parking", tags=["parking"])


@router.post("/entry")
async def park_entry(user_id: int = Depends(auth_service.get_current_user), photo: UploadFile = File(...), plate_number: str = Form(None), session: AsyncSession = Depends(get_db)):
    try:
        
        async with asynctempfile.NamedTemporaryFile(delete=False) as temp_file:
            await temp_file.write(await photo.read())
            file_path = temp_file.name

        img_processed, recognized_symbols = await plate_recognize(file_path)        

        if not recognized_symbols and not plate_number:
            raise HTTPException(status_code=400, detail="Номерний знак не розпізнано і не введено вручну")
        
        img_url, cloudinary_public_id = await cloud_service.upload_picture(img_processed, 'Entry_photos')

        
        picture = await create_picture(session, recognized_symbols, img_url, cloudinary_public_id)

        history = await create_entry(recognized_symbols or plate_number, picture.id, session)  # Виклик функції create_entry

        return {"message": "Запис успішно створено", "image_url": img_url, "plate_number": recognized_symbols or plate_number}
    #TODO create scheme
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


@router.post("/exit")
async def park_exit(user_id: int = Depends(auth_service.get_current_user), photo: UploadFile = File(...), plate_number: str = Form(None), session: AsyncSession = Depends(get_db)):

    try:
        async with asynctempfile.NamedTemporaryFile(delete=False) as temp_file:
            await temp_file.write(await photo.read())
            file_path = temp_file.name

        img_processed, recognized_symbols = await plate_recognize(file_path)        

        if not recognized_symbols and not plate_number:
            raise HTTPException(status_code=400, detail="Номерний знак не розпізнано і не введено вручну")
        
        img_url, cloudinary_public_id = await cloud_service.upload_picture(img_processed, 'Entry_photos')
        
        picture = await create_picture(session, recognized_symbols, img_url, cloudinary_public_id)

        history = await create_exit(recognized_symbols or plate_number, picture.id, session)

        return {"message": "Виїзд успішно зареєстровано", "image_url": img_url, "plate_number": recognized_symbols or plate_number}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
