"""
Web配置
FastAPI和Web界面相关配置
"""
from config.base import *

# API服务配置
API_HOST = os.getenv('API_HOST', '0.0.0.0')
API_PORT = int(os.getenv('API_PORT', '8080'))
API_DEBUG = os.getenv('API_DEBUG', 'false').lower() == 'true'
API_RELOAD = os.getenv('API_RELOAD', 'false').lower() == 'true'

# API版本
API_VERSION = 'v1'
API_PREFIX = f'/api/{API_VERSION}'

# CORS配置
CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ['*']
CORS_ALLOW_HEADERS = ['*']

# 静态文件配置
STATIC_DIR = os.path.join(BASE_DIR, 'web', 'frontend', 'dist')

# 认证配置（未来扩展）
AUTH_ENABLED = os.getenv('AUTH_ENABLED', 'false').lower() == 'true'
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')

# 限流配置（未来扩展）
RATE_LIMIT_ENABLED = False
RATE_LIMIT_PER_MINUTE = 60
