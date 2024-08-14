import os
from models import Base
from config import server_type
from sshtunnel import SSHTunnelForwarder
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

postgresql_port = ''
if server_type == 'local':
    tunnel = SSHTunnelForwarder((os.environ['SSH_HOST'], int(os.environ['SSH_PORT'])),
                                remote_bind_address=('127.0.0.1', 5432),
                                ssh_username=os.environ['SSH_USER'],
                                ssh_password=os.environ['SSH_PASS'])
    tunnel.start()
    postgresql_port = f':{tunnel.local_bind_port}'
    print(f'Connected to SSH tunnel PORT{postgresql_port}')

DATABASE_URL = f'postgresql+asyncpg://postgres:ixlrJ643b9ait2e2@localhost{postgresql_port}/media_db'

engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def database_connect():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
