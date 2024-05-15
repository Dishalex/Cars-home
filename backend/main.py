from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.database.db import get_db
from backend.src.routes import auth_routes, admin_routes, user_routes, history_routes, parking_routes, tg_routes, picture_routes

app = FastAPI()

app.include_router(auth_routes.router, prefix="/api")
app.include_router(admin_routes.router, prefix="/api")
app.include_router(user_routes.router, prefix="/api")
app.include_router(history_routes.router, prefix="/api")
app.include_router(parking_routes.router, prefix="/api")
app.include_router(tg_routes.router, prefix="/api")
app.include_router(picture_routes.router, prefix="/api")


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
