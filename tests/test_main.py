import os
import pytest
from main import app
from uuid import uuid4
from models import MediaFile
from httpx import AsyncClient
from database import SessionLocal
from sqlalchemy.future import select


@pytest.mark.asyncio
async def test_file_not_found():
    """Тест на получение метаданных несуществующего файла"""

    async with AsyncClient(app=app, base_url='http://localhost') as ac:
        response = await ac.get(f'/files/{str(uuid4())}')

    assert response.status_code == 404
    assert response.json() == {'detail': 'File not found'}


@pytest.mark.asyncio
async def test_file_upload():
    """Тест на загрузку файла и сохранение его метаданных в базу данных"""
    temp_file_name = 'temp_test_file.txt'
    with open(temp_file_name, 'w') as temp_file:
        temp_file.write('This is a test file')

    async with AsyncClient(app=app, base_url='http://localhost') as ac:
        with open(temp_file_name, 'rb') as temp_file:
            response = await ac.post('/upload/', files={'file': temp_file})

    assert response.status_code == 200
    json_response = response.json()

    assert 'id' in json_response

    async with SessionLocal() as session:
        result = await session.execute(select(MediaFile).where(MediaFile.id == json_response['id']))
        media_file = result.scalars().one_or_none()

    assert media_file is not None
    assert media_file.original_name == temp_file_name
    assert media_file.extension == '.txt'

    os.remove(temp_file_name)


@pytest.mark.asyncio
async def test_file_metadata_retrieval():
    """Тест на получение метаданных файла по его ID"""
    uid = str(uuid4())

    async with SessionLocal() as session:
        session.add(MediaFile(
                id=uid,
                file_size=1024,
                extension='.txt',
                file_format='text/plain',
                original_name='test_file.txt',
        ))
        await session.commit()

    async with AsyncClient(app=app, base_url='http://localhost') as ac:
        response = await ac.get(f'/files/{uid}')

    assert response.status_code == 200
    json_response = response.json()

    assert json_response['id'] == uid
    assert json_response['extension'] == '.txt'
    assert json_response['original_name'] == 'test_file.txt'
