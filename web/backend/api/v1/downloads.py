"""
下载相关API
"""
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import Response
from core.models.database import Database
from core.services.node_service import NodeService
from core.services.config_service import ConfigService

router = APIRouter()


@router.get("/nodes/{node_id}/config")
async def download_config(node_id: int):
    """下载节点配置文件"""
    try:
        with Database() as db:
            config_service = ConfigService(db)
            node_service = NodeService(db)
            
            # 获取节点信息
            node = node_service.get_node(node_id=node_id)
            if not node:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"节点 ID {node_id} 不存在"
                )
            
            # 生成配置
            config_content = config_service.generate_client_config(node_id)
            
            return Response(
                content=config_content,
                media_type="text/plain",
                headers={
                    "Content-Disposition": f'attachment; filename="{node.node_name}.conf"'
                }
            )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/nodes/{node_id}/script")
async def download_script(node_id: int, server_api: str = "http://SERVER_IP:8080"):
    """下载节点安装脚本"""
    try:
        with Database() as db:
            config_service = ConfigService(db)
            node_service = NodeService(db)
            
            # 获取节点信息
            node = node_service.get_node(node_id=node_id)
            if not node:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"节点 ID {node_id} 不存在"
                )
            
            # 生成脚本
            script_content = config_service.generate_install_script(node_id, server_api)
            
            # 确定文件名和MIME类型
            if node.platform == 'linux':
                filename = f"{node.node_name}-install.sh"
                media_type = "text/x-shellscript"
            else:  # windows
                filename = f"{node.node_name}-install.ps1"
                media_type = "text/plain"
            
            return Response(
                content=script_content,
                media_type=media_type,
                headers={
                    "Content-Disposition": f'attachment; filename="{filename}"'
                }
            )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
