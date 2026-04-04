import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    NOTION_TOKEN = os.getenv('NOTION_TOKEN')
    DATABASE_ID = os.getenv('NOTION_DATABASE_ID')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # Cache settings (in seconds)
    CACHE_TIMEOUT = int(os.getenv('CACHE_TIMEOUT', 3600))  # Default 1 hour
    
    # Blog details
    BLOG_NAME = os.getenv('BLOG_NAME', 'Akita Inspired Blog')
    BLOG_DESCRIPTION = os.getenv('BLOG_DESCRIPTION', 'A minimalist blog powered by Notion API.')
    BASE_URL = os.getenv('BASE_URL', 'http://localhost:5000')
