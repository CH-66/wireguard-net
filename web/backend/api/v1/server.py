"""
服务端管理API
"""
from fastapi import APIRouter, HTTPException, status
from core.models.database import Database
from core.services.server_service import ServerService
from web.backend.schemas.server import ServerInitRequest, ServerResponse, ServerStatusResponse
from web.backend.schemas.common import MessageResponse

router = APIRouter()


@router.post("/server/init", response_model=ServerResponse, status_code=status.HTTP_201_CREATED)
async def initialize_server(request: ServerInitRequest):
    """初始化服务端"""
    try:
        with Database() as db:
            server_service = ServerService(db)
            server = server_service.initialize_server(
                listen_port=request.listen_port,
                network_cidr=request.network_cidr,
                server_ip=request.server_ip,
                public_endpoint=request.public_endpoint,
                force=request.force
            )
            
            return ServerResponse(
                id=server.id,
                virtual_ip=server.virtual_ip,
                listen_port=server.listen_port,
                network_cidr=server.network_cidr,
                public_key=server.public_key,
                public_endpoint=server.public_endpoint,
                created_at=server.created_at
            )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/server/info", response_model=ServerResponse)
async def get_server_info():
    """获取服务端信息"""
    try:
        with Database() as db:
            server_service = ServerService(db)
            server = server_service.get_server_info()
            
            if not server:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="服务端未初始化"
                )
            
            return ServerResponse(
                id=server.id,
                virtual_ip=server.virtual_ip,
                listen_port=server.listen_port,
                network_cidr=server.network_cidr,
                public_key=server.public_key,
                public_endpoint=server.public_endpoint,
                created_at=server.created_at
            )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/server/reload", response_model=MessageResponse)
async def reload_wireguard():
    """重载WireGuard配置"""
    try:
        with Database() as db:
            server_service = ServerService(db)
            server_service.reload_wireguard()
            return MessageResponse(message="WireGuard配置重载成功")
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/server/status", response_model=ServerStatusResponse)
async def get_server_status():
    """获取服务端运行状态"""
    try:
        with Database() as db:
            server_service = ServerService(db)
            status_info = server_service.get_status()
            
            return ServerStatusResponse(
                wireguard_running=status_info['wireguard_running'],
                interface_name=status_info['interface_name'],
                total_nodes=status_info['total_nodes'],
                connected_peers=status_info['connected_peers']
            )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
