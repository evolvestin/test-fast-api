import asyncio
from pathlib import Path
from base import base_dir
from models import MediaFile
from database import SessionLocal
from sqlalchemy.future import select
from datetime import datetime, timedelta

FILE_EXPIRATION_DAYS = 30  # Время жизни файла в днях (например, 30 дней)


async def cleanup_files():
    expiration_time = datetime.now() - timedelta(days=FILE_EXPIRATION_DAYS)

    async with SessionLocal() as db:
        # Получаем все файлы из базы данных, которые старше определенного времени
        result = await db.execute(select(MediaFile).where(MediaFile.file_size > 0))
        media_files = result.scalars().all()

        for media_file in media_files:
            file_path = Path(f'{base_dir.joinpath('media')}/{media_file.id}{media_file.extension}')
            if file_path.exists() and datetime.fromtimestamp(file_path.stat().st_mtime) < expiration_time:
                try:
                    file_path.unlink()  # Удаляем файл с диска
                    db.delete(media_file)  # Удаляем запись о файле из базы данных
                    await db.commit()
                    print(f'Deleted {file_path}')
                except Exception as e:
                    print(f'Error deleting file {file_path}: {e}')

if __name__ == '__main__':
    asyncio.run(cleanup_files())
