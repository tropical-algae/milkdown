from sqlalchemy.orm import sessionmaker
from sqlmodel import Session, create_engine
from sqlmodel import SQLModel
from milkdown.common.config import settings
from milkdown.common.logging import logger

local_engine = create_engine(url=settings.SQL_DATABASE_URI, pool_pre_ping=True, echo=settings.DEBUG)
LocalSession = sessionmaker(autocommit=False, autoflush=False, bind=local_engine, class_=Session)

logger.info(f"[init] Checking database consistency...")
SQLModel.metadata.create_all(local_engine)

