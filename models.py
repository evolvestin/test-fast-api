from sqlalchemy import Column, String, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()


class MediaFile(Base):
    __tablename__ = 'media_files'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    original_name = Column(String, nullable=False)
    file_size = Column(BigInteger, nullable=False)
    file_format = Column(String, nullable=False)
    extension = Column(String, nullable=False)
