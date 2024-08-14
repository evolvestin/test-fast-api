import os
import aiohttp
import aiofiles
from uuid import uuid4
from base import base_dir
from models import MediaFile
from sqlalchemy.future import select
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from database import SessionLocal, database_connect
from fastapi import FastAPI, UploadFile, HTTPException, Depends

# Проверка существования папки media в месте со скриптом
os.mkdir(base_dir.joinpath('media')) if 'media' not in os.listdir(base_dir.joinpath('')) else None


async def get_db():
    async with SessionLocal() as session:
        yield session


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await database_connect()  # Инициализация базы данных при запуске приложения
    yield

app = FastAPI(lifespan=lifespan)


@app.post('/upload/', response_model=dict)  # Метод загрузки файла
async def upload_file(file: UploadFile, db: AsyncSession = Depends(get_db)):
    uid = str(uuid4())
    file_extension = os.path.splitext(file.filename)[1]
    save_path = f"{base_dir.joinpath('media')}/{uid}{file_extension}"  # Путь до файла (куда сохраняем)

    try:
        async with aiofiles.open(save_path, 'wb') as out_file:  # Сохранение файла на диск
            while chunk := await file.read(1024):  # Чтение файла по частям (по 1024 байта)
                await out_file.write(chunk)

        db.add(MediaFile(  # Сохранение метаданных в базу данных
            id=uid,
            extension=file_extension,
            original_name=file.filename,
            file_format=file.content_type,
            file_size=os.path.getsize(save_path),
        ))
        await db.commit()

        async with aiohttp.ClientSession() as session:  # Асинхронная отправка файла в облако
            async with session.post('https://cloud-storage.com/upload',
                                    data={'file': open(save_path, 'rb')}) as response:
                if response.status != 200:  # Если загрузка файла прошла не успешно, выдаем ошибку
                    raise HTTPException(status_code=500, detail='Failed to upload to cloud')
        return {'id': uid}

    except Exception as error:
        raise HTTPException(status_code=500, detail=f'File upload failed: {error}')


@app.get('/files/{file_id}')  # Получение метаданных файла
async def get_file(file_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MediaFile).where(MediaFile.id == file_id))
    media_file = result.scalar_one_or_none()
    if media_file is None:  # Если файл не найден в базе по file_id, выдаем ошибку
        raise HTTPException(status_code=404, detail='File not found')
    return media_file
