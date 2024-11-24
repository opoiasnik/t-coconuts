from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Настройка базы данных
DATABASE_URL = "sqlite:///requests.db"  # Путь к базе данных SQLite
engine = create_engine(DATABASE_URL, echo=False)
Base = declarative_base()

# Определение модели
class UserRequest(Base):
    __tablename__ = 'user_requests'

    id = Column(Integer, primary_key=True, autoincrement=True)
    endpoint = Column(String(255), nullable=False)
    request_data = Column(Text, nullable=False)
    response_data = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

# Создание таблиц
Base.metadata.create_all(engine)

# Настройка сессии
Session = sessionmaker(bind=engine)
session = Session()
