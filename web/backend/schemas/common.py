"""
公共数据模型
"""
from typing import Optional
from pydantic import BaseModel


class MessageResponse(BaseModel):
    """消息响应"""
    message: str


class ErrorResponse(BaseModel):
    """错误响应"""
    error_code: str
    message: str
