"""
HTTP API 服务模块
提供 RESTful API 接口
"""
from flask import Flask, jsonify, request, send_file, Response
from typing import Dict, Any, Optional
import io
from database import Database
from node_manager import NodeManager
import config


app = Flask(__name__)


def success_response(data: Any) -> Dict[str, Any]:
    """成功响应格式
    
    Args:
        data: 响应数据
        
    Returns:
        响应字典
    """
    return {
        'status': 'success',
        'data': data
    }


def error_response(error_code: str, message: str) -> Dict[str, Any]:
    """错误响应格式
    
    Args:
        error_code: 错误码
        message: 错误信息
        
    Returns:
        响应字典
    """
    return {
        'status': 'error',
        'error_code': error_code,
        'message': message
    }


@app.route('/')
def index():
    """API 根路径"""
    return jsonify({
        'name': 'WireGuard Network Toolkit API',
        'version': '1.0.0',
        'endpoints': {
            'register_node': 'POST /api/nodes/register',
            'list_nodes': 'GET /api/nodes/list',
            'get_node': 'GET /api/nodes/<node_id>',
            'delete_node': 'DELETE /api/nodes/<node_id>',
            'download_config': 'GET /api/download/config/<node_name>',
            'download_script': 'GET /api/download/script/<node_name>',
        }
    })


@app.route('/api/nodes/register', methods=['POST'])
def register_node():
    """注册新节点"""
    try:
        # 获取请求参数
        data = request.get_json()
        if not data:
            return jsonify(error_response(
                'INVALID_PARAMETER',
                '请求体不能为空'
            )), 400
            
        node_name = data.get('node_name')
        platform = data.get('platform')
        description = data.get('description')
        
        # 参数验证
        if not node_name:
            return jsonify(error_response(
                'INVALID_PARAMETER',
                '节点名称不能为空'
            )), 400
            
        if not platform:
            return jsonify(error_response(
                'INVALID_PARAMETER',
                '平台类型不能为空'
            )), 400
            
        if platform not in ['linux', 'windows']:
            return jsonify(error_response(
                'INVALID_PARAMETER',
                '平台类型必须为 linux 或 windows'
            )), 400
            
        # 注册节点
        with Database() as db:
            node_manager = NodeManager(db)
            
            try:
                result = node_manager.register_node(
                    node_name=node_name,
                    platform=platform,
                    description=description
                )
                
                # 不返回私钥和完整配置（仅通过下载接口获取）
                response_data = {
                    'node_id': result['node_id'],
                    'node_name': result['node_name'],
                    'virtual_ip': result['virtual_ip'],
                    'public_key': result['public_key'],
                    'platform': result['platform'],
                    'description': result['description'],
                    'created_at': result['created_at'],
                    'download_urls': {
                        'config': f'/api/download/config/{node_name}',
                        'script': f'/api/download/script/{node_name}'
                    }
                }
                
                return jsonify(success_response(response_data)), 201
                
            except ValueError as e:
                error_code = 'NODE_ALREADY_EXISTS' if '已存在' in str(e) else 'INVALID_PARAMETER'
                return jsonify(error_response(error_code, str(e))), 400
            except RuntimeError as e:
                if 'IP 地址池已耗尽' in str(e):
                    return jsonify(error_response('IP_POOL_EXHAUSTED', str(e))), 500
                return jsonify(error_response('INTERNAL_ERROR', str(e))), 500
                
    except Exception as e:
        return jsonify(error_response('INTERNAL_ERROR', f'服务器内部错误: {str(e)}')), 500


@app.route('/api/nodes/list', methods=['GET'])
def list_nodes():
    """获取所有节点列表"""
    try:
        with Database() as db:
            nodes = db.get_all_nodes()
            
            # 不返回私钥信息
            safe_nodes = []
            for node in nodes:
                safe_node = {
                    'id': node['id'],
                    'node_name': node['node_name'],
                    'virtual_ip': node['virtual_ip'],
                    'public_key': node['public_key'],
                    'platform': node['platform'],
                    'description': node['description'],
                    'created_at': node['created_at']
                }
                safe_nodes.append(safe_node)
                
            return jsonify(success_response(safe_nodes)), 200
            
    except Exception as e:
        return jsonify(error_response('INTERNAL_ERROR', f'服务器内部错误: {str(e)}')), 500


@app.route('/api/nodes/<int:node_id>', methods=['GET'])
def get_node(node_id: int):
    """获取指定节点详情"""
    try:
        with Database() as db:
            node = db.get_node_by_id(node_id)
            
            if not node:
                return jsonify(error_response(
                    'NODE_NOT_FOUND',
                    f'节点 ID {node_id} 不存在'
                )), 404
                
            # 包含私钥的详细信息（谨慎使用）
            return jsonify(success_response(dict(node))), 200
            
    except Exception as e:
        return jsonify(error_response('INTERNAL_ERROR', f'服务器内部错误: {str(e)}')), 500


@app.route('/api/nodes/<int:node_id>', methods=['DELETE'])
def delete_node(node_id: int):
    """删除指定节点"""
    try:
        with Database() as db:
            node_manager = NodeManager(db)
            
            try:
                success = node_manager.delete_node(node_id)
                
                if success:
                    return jsonify(success_response({
                        'message': f'节点 {node_id} 删除成功'
                    })), 200
                else:
                    return jsonify(error_response(
                        'INTERNAL_ERROR',
                        '删除失败'
                    )), 500
                    
            except ValueError as e:
                return jsonify(error_response('NODE_NOT_FOUND', str(e))), 404
                
    except Exception as e:
        return jsonify(error_response('INTERNAL_ERROR', f'服务器内部错误: {str(e)}')), 500


@app.route('/api/download/config/<node_name>', methods=['GET'])
def download_config(node_name: str):
    """下载节点配置文件"""
    try:
        with Database() as db:
            node = db.get_node_by_name(node_name)
            
            if not node:
                return jsonify(error_response(
                    'NODE_NOT_FOUND',
                    f'节点 {node_name} 不存在'
                )), 404
                
            server_info = db.get_server_info()
            if not server_info:
                return jsonify(error_response(
                    'INTERNAL_ERROR',
                    '服务端未初始化'
                )), 500
                
            # 生成配置文件
            from config_generator import ConfigGenerator
            generator = ConfigGenerator()
            
            dns_server = db.get_config_param('dns_server') or config.DEFAULT_DNS_SERVER
            config_content = generator.generate_client_config(
                node_info=node,
                server_info=server_info,
                dns_server=dns_server
            )
            
            # 返回配置文件
            return Response(
                config_content,
                mimetype='text/plain',
                headers={
                    'Content-Disposition': f'attachment; filename={node_name}.conf'
                }
            )
            
    except Exception as e:
        return jsonify(error_response('INTERNAL_ERROR', f'服务器内部错误: {str(e)}')), 500


@app.route('/api/download/script/<node_name>', methods=['GET'])
def download_script(node_name: str):
    """下载节点接入脚本"""
    try:
        with Database() as db:
            node = db.get_node_by_name(node_name)
            
            if not node:
                return jsonify(error_response(
                    'NODE_NOT_FOUND',
                    f'节点 {node_name} 不存在'
                )), 404
                
            # 生成脚本
            from config_generator import ConfigGenerator
            generator = ConfigGenerator()
            
            # 获取服务端 API 地址（从请求中推断）
            server_api = f"{request.scheme}://{request.host}"
            
            if node['platform'] == 'linux':
                script_content = generator.generate_linux_install_script(
                    node_name=node_name,
                    server_api=server_api
                )
                filename = f'{node_name}-install.sh'
                mimetype = 'text/x-shellscript'
            else:  # windows
                script_content = generator.generate_windows_install_script(
                    node_name=node_name,
                    server_api=server_api
                )
                filename = f'{node_name}-install.ps1'
                mimetype = 'text/plain'
                
            # 返回脚本文件
            return Response(
                script_content,
                mimetype=mimetype,
                headers={
                    'Content-Disposition': f'attachment; filename={filename}'
                }
            )
            
    except Exception as e:
        return jsonify(error_response('INTERNAL_ERROR', f'服务器内部错误: {str(e)}')), 500


def run_api_server(host: Optional[str] = None, port: Optional[int] = None, debug: bool = False):
    """启动 API 服务
    
    Args:
        host: 监听地址
        port: 监听端口
        debug: 是否调试模式
    """
    host = host or config.API_HOST
    port = port or config.API_PORT
    
    print("========================================")
    print("WireGuard Network Toolkit API Server")
    print("========================================")
    print(f"监听地址: {host}:{port}")
    print("========================================")
    print()
    print("API 端点:")
    print("  POST   /api/nodes/register         - 注册节点")
    print("  GET    /api/nodes/list             - 列出所有节点")
    print("  GET    /api/nodes/<node_id>        - 获取节点详情")
    print("  DELETE /api/nodes/<node_id>        - 删除节点")
    print("  GET    /api/download/config/<name> - 下载配置文件")
    print("  GET    /api/download/script/<name> - 下载接入脚本")
    print("========================================")
    print()
    
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    run_api_server()
