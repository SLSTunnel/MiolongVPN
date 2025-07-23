from sqlalchemy import Column, Integer, String, Boolean, create_engine, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    is_admin = Column(Boolean, default=False)
    expiration_date = Column(DateTime, nullable=True)
    last_login = Column(DateTime, nullable=True)
    email = Column(String, unique=True, nullable=True)
    language = Column(String, default='en')

# SQLite for demo; switch to MySQL/Postgres for production
database_url = 'sqlite:///./miolongvpn.db'
engine = create_engine(database_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 