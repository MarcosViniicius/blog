import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    NOTION_TOKEN = os.getenv('NOTION_TOKEN')
    DATABASE_ID = os.getenv('NOTION_DATABASE_ID')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # Cache settings (in seconds)
    CACHE_TYPE = os.getenv('CACHE_TYPE', 'FileSystemCache')
    
    # Vercel has a read-only filesystem except for /tmp
    if os.getenv('VERCEL'):
        CACHE_DIR = '/tmp/.flask_cache'
    else:
        CACHE_DIR = os.getenv('CACHE_DIR', '.flask_cache')
        
    CACHE_LIST_TIMEOUT = int(os.getenv('CACHE_LIST_TIMEOUT', 300))  # 5 minutes
    CACHE_POST_TIMEOUT = int(os.getenv('CACHE_POST_TIMEOUT', 86400)) # 24 hours
    
    # Blog details
    BLOG_NAME = os.getenv('BLOG_NAME', 'Marcos Tech Blog')
    BLOG_DESCRIPTION = os.getenv('BLOG_DESCRIPTION', 'A minimalist blog powered by Notion API.')
    BASE_URL = os.getenv('BASE_URL', 'http://localhost:5000')
