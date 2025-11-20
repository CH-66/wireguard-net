"""
FastAPI应用入口
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from web.backend.api.v1 import nodes, server, downloads
from config import web as config

# 创建FastAPI应用
app = FastAPI(
    title="WireGuard Network Toolkit API",
    description="WireGuard快速组网工具API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=config.CORS_ALLOW_CREDENTIALS,
    allow_methods=config.CORS_ALLOW_METHODS,
    allow_headers=config.CORS_ALLOW_HEADERS,
)

# 注册路由
app.include_router(nodes.router, prefix=config.API_PREFIX, tags=["nodes"])
app.include_router(server.router, prefix=config.API_PREFIX, tags=["server"])
app.include_router(downloads.router, prefix=config.API_PREFIX, tags=["downloads"])


@app.get("/")
async def root():
    """API根路径"""
    return {
        "name": "WireGuard Network Toolkit API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=config.API_RELOAD
    )
