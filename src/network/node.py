"""
Decentralized AI Network Node
P2P网络节点实现
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class NodeInfo:
    """节点信息"""
    node_id: str
    address: str
    port: int
    role: str  # 'provider', 'requester', 'validator'
    compute_power: float  # TFLOPs
    reputation: float  # 0-100
    stake_amount: float  # 质押的DAIC数量


class NetworkNode:
    """P2P网络节点"""
    
    def __init__(self, node_id: str, host: str = "0.0.0.0", port: int = 8000):
        self.node_id = node_id
        self.host = host
        self.port = port
        self.peers: Dict[str, NodeInfo] = {}
        self.tasks: Dict[str, dict] = {}
        self.is_running = False
        
    async def start(self):
        """启动节点"""
        self.is_running = True
        logger.info(f"Node {self.node_id} started on {self.host}:{self.port}")
        
        # 启动服务器
        server = await asyncio.start_server(
            self._handle_connection, self.host, self.port
        )
        
        async with server:
            await server.serve_forever()
    
    async def _handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """处理连接"""
        addr = writer.get_extra_info('peername')
        logger.info(f"Connection from {addr}")
        
        try:
            while self.is_running:
                data = await reader.read(4096)
                if not data:
                    break
                
                message = json.loads(data.decode())
                await self._process_message(message, writer)
                
        except Exception as e:
            logger.error(f"Connection error: {e}")
        finally:
            writer.close()
            await writer.wait_closed()
    
    async def _process_message(self, message: dict, writer: asyncio.StreamWriter):
        """处理消息"""
        msg_type = message.get('type')
        
        if msg_type == 'ping':
            response = {'type': 'pong', 'node_id': self.node_id}
            writer.write(json.dumps(response).encode())
            await writer.drain()
            
        elif msg_type == 'discover':
            # 返回已知节点列表
            response = {
                'type': 'peers',
                'peers': [
                    {
                        'node_id': peer.node_id,
                        'address': peer.address,
                        'port': peer.port,
                        'role': peer.role
                    }
                    for peer in self.peers.values()
                ]
            }
            writer.write(json.dumps(response).encode())
            await writer.drain()
            
        elif msg_type == 'task_request':
            # 处理任务请求
            await self._handle_task_request(message, writer)
            
        elif msg_type == 'task_result':
            # 处理任务结果
            await self._handle_task_result(message, writer)
    
    async def _handle_task_request(self, message: dict, writer: asyncio.StreamWriter):
        """处理任务请求"""
        task_id = message.get('task_id')
        task_data = message.get('data')
        
        logger.info(f"Received task request: {task_id}")
        
        # 存储任务
        self.tasks[task_id] = {
            'data': task_data,
            'status': 'pending',
            'created_at': datetime.now().isoformat()
        }
        
        # 返回确认
        response = {
            'type': 'task_accepted',
            'task_id': task_id,
            'node_id': self.node_id
        }
        writer.write(json.dumps(response).encode())
        await writer.drain()
    
    async def _handle_task_result(self, message: dict, writer: asyncio.StreamWriter):
        """处理任务结果"""
        task_id = message.get('task_id')
        result = message.get('result')
        
        logger.info(f"Received task result: {task_id}")
        
        if task_id in self.tasks:
            self.tasks[task_id]['result'] = result
            self.tasks[task_id]['status'] = 'completed'
    
    async def connect_to_peer(self, host: str, port: int):
        """连接到其他节点"""
        try:
            reader, writer = await asyncio.open_connection(host, port)
            
            # 发送ping
            message = {'type': 'ping', 'node_id': self.node_id}
            writer.write(json.dumps(message).encode())
            await writer.drain()
            
            # 等待响应
            data = await reader.read(4096)
            response = json.loads(data.decode())
            
            if response.get('type') == 'pong':
                peer_id = response.get('node_id')
                logger.info(f"Connected to peer: {peer_id}")
                
                # 添加到peers列表
                self.peers[peer_id] = NodeInfo(
                    node_id=peer_id,
                    address=host,
                    port=port,
                    role='unknown',
                    compute_power=0.0,
                    reputation=50.0,
                    stake_amount=0.0
                )
            
            writer.close()
            await writer.wait_closed()
            
        except Exception as e:
            logger.error(f"Failed to connect to peer {host}:{port}: {e}")
    
    def get_node_info(self) -> dict:
        """获取节点信息"""
        return {
            'node_id': self.node_id,
            'host': self.host,
            'port': self.port,
            'peers_count': len(self.peers),
            'tasks_count': len(self.tasks)
        }


async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Decentralized AI Network Node')
    parser.add_argument('--node-id', default='node1', help='Node ID')
    parser.add_argument('--host', default='0.0.0.0', help='Host address')
    parser.add_argument('--port', type=int, default=8000, help='Port number')
    parser.add_argument('--role', default='provider', choices=['provider', 'requester', 'validator'])
    
    args = parser.parse_args()
    
    node = NetworkNode(args.node_id, args.host, args.port)
    
    logger.info(f"Starting node as {args.role}")
    logger.info(f"Node info: {node.get_node_info()}")
    
    await node.start()


if __name__ == '__main__':
    asyncio.run(main())
