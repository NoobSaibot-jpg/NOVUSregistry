from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from configparser import ConfigParser
import os

# Загрузка конфигурации
config = ConfigParser()
config.read('config.ini')
DATABASE_URL = config.get('database', 'url')

# Создание движка базы данных
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 