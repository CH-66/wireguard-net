"""
节点管理API
"""
from typing import List
from fastapi import APIRouter, HTTPException, status
from core.models.database import Database
from core.services.node_service import NodeService
from web.backend.schemas.node import NodeCreateRequest, NodeResponse, NodeDetailResponse
from web.backend.schemas.common import MessageResponse

router = APIRouter()


@router.post("/nodes", response_model=NodeResponse, status_code=status.HTTP_201_CREATED)
async def create_node(request: NodeCreateRequest):
    """注册新节点"""
    try:
        with Database() as db:
            node_service = NodeService(db)
            result = node_service.register_node(
                node_name=request.node_name,
                platform=request.platform,
                description=request.description
            )
            
            # 获取节点信息
            node = node_service.get_node(node_id=result['node_id'])
            if not node:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="节点创建成功但无法获取信息"
                )
            
            return NodeResponse(
                id=node.id,
                node_name=node.node_name,
                virtual_ip=node.virtual_ip,
                public_key=node.public_key,
                platform=node.platform,
                description=node.description,
                created_at=node.created_at,
                updated_at=node.updated_at
            )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/nodes", response_model=List[NodeResponse])
async def list_nodes():
    """获取所有节点列表"""
    try:
        with Database() as db:
            node_service = NodeService(db)
            nodes = node_service.list_nodes()
            
            return [
                NodeResponse(
                    id=node.id,
                    node_name=node.node_name,
                    virtual_ip=node.virtual_ip,
                    public_key=node.public_key,
                    platform=node.platform,
                    description=node.description,
                    created_at=node.created_at,
                    updated_at=node.updated_at
                )
                for node in nodes
            ]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/nodes/{node_id}", response_model=NodeDetailResponse)
async def get_node(node_id: int):
    """获取节点详情"""
    try:
        with Database() as db:
            node_service = NodeService(db)
            node = node_service.get_node(node_id=node_id)
            
            if not node:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"节点 ID {node_id} 不存在"
                )
            
            return NodeDetailResponse(
                id=node.id,
                node_name=node.node_name,
                virtual_ip=node.virtual_ip,
                public_key=node.public_key,
                private_key=node.private_key,
                platform=node.platform,
                description=node.description,
                created_at=node.created_at,
                updated_at=node.updated_at
            )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/nodes/{node_id}", response_model=MessageResponse)
async def delete_node(node_id: int):
    """删除节点"""
    try:
        with Database() as db:
            node_service = NodeService(db)
            success = node_service.delete_node(node_id)
            
            if success:
                return MessageResponse(message=f"节点 {node_id} 删除成功")
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="删除失败"
                )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
