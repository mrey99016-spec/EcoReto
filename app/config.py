import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-ecoreto')
    DATABASE_URL = os.environ.get('DATABASE_URL', '')
