# backend/main.py
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.database.db import get_db
from backend.src.routes import auth_routes, user_routes

import logging

# logging.basicConfig(level=logging.DEBUG,
#                     format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()

# Налаштування логера
logger = logging.getLogger("myapp")
logging.basicConfig(level=logging.DEBUG)

@app.exception_handler(Exception)
async def universal_exception_handler(request: Request, exc: Exception):
    """Обробник усіх винятків"""
    logger.error(f"Unhandled exception: {exc} - Path: {request.url.path}")
    # Можете додати будь-яку додаткову обробку тут
    return JSONResponse(
        status_code=500,
        content={"message": "Internal Server Error"},
    )


app.include_router(auth_routes.router, prefix="/api")
app.include_router(user_routes.router, prefix="/api")


# Health Check endpoint
@app.get("/api/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):

    try:
        result = await db.execute(text("SELECT 1"))
        result = result.fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")






