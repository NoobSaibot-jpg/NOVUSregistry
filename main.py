from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, func, or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
import sys
from typing import List, Optional
from pydantic import BaseModel
import configparser
import webbrowser
import threading
import time
import asyncio
from hypercorn.config import Config
from hypercorn.asyncio import serve

# Определяем путь к ресурсам в зависимости от того, запущено ли приложение как exe
def get_resource_path(relative_path):
    try:
        # PyInstaller создает временную папку и хранит путь в _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Чтение конфигурации
def load_config():
    config = configparser.ConfigParser()
    config_path = get_resource_path('config.ini')
    config.read(config_path)
    return {
        'host': config.get('server', 'host'),
        'port': int(config.get('server', 'port')),
        'database_url': config.get('database', 'url')
    }

# Загружаем конфигурацию
config = load_config()
HOST = config['host']
PORT = config['port']
DATABASE_URL = config['database_url']

# Настройка базы данных
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Модель проекта
class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String)
    category = Column(String)
    project_type = Column(String)
    stage = Column(String)
    project_code_full = Column(String)
    project_code_short = Column(String)
    project_name = Column(String)
    sheet_number = Column(String)
    is_separate_doc = Column(Boolean)
    box_number = Column(String)
    folder_number = Column(String)
    file_path = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

# Pydantic модели
class ProjectBase(BaseModel):
    id: int
    file_name: str
    category: str
    project_type: str
    stage: str
    project_code_full: str
    project_code_short: str
    project_name: str
    sheet_number: str
    is_separate_doc: bool
    box_number: str
    folder_number: str
    file_path: str
    created_at: datetime

    class Config:
        orm_mode = True

class ProjectResponse(BaseModel):
    items: List[ProjectBase]
    total: int

# Создание таблиц
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Монтирование статических файлов
static_path = get_resource_path('static')
app.mount("/static", StaticFiles(directory=static_path), name="static")

@app.get("/")
async def read_root():
    return FileResponse(os.path.join(static_path, 'index.html'))

@app.get("/api/projects/", response_model=ProjectResponse)
async def get_projects(
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    db = SessionLocal()
    try:
        query = db.query(Project)
        
        if search:
            search_filter = or_(
                Project.file_name.ilike(f"%{search}%"),
                Project.category.ilike(f"%{search}%"),
                Project.project_type.ilike(f"%{search}%"),
                Project.stage.ilike(f"%{search}%"),
                Project.project_code_short.ilike(f"%{search}%"),
                Project.project_name.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        total = query.count()
        projects = query.offset(skip).limit(limit).all()
        
        return {
            "items": projects,
            "total": total
        }
    finally:
        db.close()

@app.get("/api/projects/{project_id}/download")
async def download_file(project_id: int, view: bool = False):
    db = SessionLocal()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        if not os.path.exists(project.file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        # Получаем расширение файла
        file_name, file_extension = os.path.splitext(project.file_name)
        
        # Очищаем имя файла от подчеркиваний в начале и конце
        clean_name = file_name.strip('_')
        clean_extension = file_extension.strip('_')
        clean_filename = f"{clean_name}{clean_extension}"
        
        # Отладочная информация
        print(f"Original filename: {project.file_name}")
        print(f"Cleaned filename: {clean_filename}")
        
        # Определяем MIME-тип в зависимости от расширения
        mime_types = {
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.xls': 'application/vnd.ms-excel',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.txt': 'text/plain',
        }
        
        media_type = mime_types.get(clean_extension.lower(), 'application/octet-stream')
        
        response = FileResponse(
            project.file_path,
            media_type=media_type
        )
        
        # Формируем заголовок Content-Disposition без кавычек
        disposition = f'attachment; filename={clean_filename}'
        response.headers["Content-Disposition"] = disposition
        
        return response
    finally:
        db.close()

async def run_server():
    config = Config()
    config.bind = [f"{HOST}:{PORT}"]
    config.use_reloader = False
    await serve(app, config)

if __name__ == "__main__":
    def open_browser():
        # Даем серверу время на запуск
        time.sleep(1)
        # Открываем браузер по умолчанию
        webbrowser.open(f'http://{HOST}:{PORT}')
    
    # Запускаем открытие браузера в отдельном потоке
    threading.Thread(target=open_browser).start()
    
    # Запускаем сервер
    asyncio.run(run_server()) 