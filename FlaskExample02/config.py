# 사전 설치 : pip install python-dotenv
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class Config:
    """애플리케이션 환경 설정 클래스"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')
    
    # 데이터베이스 설정
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_NAME = os.getenv('DB_NAME', 'test')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    
    DEBUG = os.getenv('FLASK_ENV') == 'development'
