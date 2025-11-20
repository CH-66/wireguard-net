"""
节点相关数据模型
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class NodeCreateRequest(BaseModel):
    """创建节点请求"""
    node_name: str = Field(..., min_length=1, max_length=100, description="节点名称")
    platform: str = Field(..., pattern="^(linux|windows)$", description="平台类型")
    description: Optional[str] = Field(None, max_length=500, description="节点描述")


class NodeResponse(BaseModel):
    """节点响应"""
    id: int
    node_name: str
    virtual_ip: str
    public_key: str
    platform: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class NodeDetailResponse(NodeResponse):
    """节点详情响应（包含私钥）"""
    private_key: Optional[str] = None
