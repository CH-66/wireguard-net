"""
服务端相关数据模型
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ServerInitRequest(BaseModel):
    """服务端初始化请求"""
    listen_port: Optional[int] = Field(51820, ge=1, le=65535, description="监听端口")
    network_cidr: Optional[str] = Field("10.0.0.0/24", description="网络段")
    server_ip: Optional[str] = Field("10.0.0.1", description="服务端虚拟IP")
    public_endpoint: Optional[str] = Field(None, description="公网地址")
    force: bool = Field(False, description="强制重新初始化")


class ServerResponse(BaseModel):
    """服务端响应"""
    id: int
    virtual_ip: str
    listen_port: int
    network_cidr: str
    public_key: str
    public_endpoint: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ServerStatusResponse(BaseModel):
    """服务端状态响应"""
    wireguard_running: bool
    interface_name: str
    total_nodes: int
    connected_peers: int
