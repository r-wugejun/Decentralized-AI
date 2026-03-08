"""
Decentralized AI - 第一步：P2P网络节点
简单易懂版本 - 让电脑互相发现
"""

import asyncio
import json
import logging
from typing import Dict, List
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SimpleNode:
    """
    简单的P2P网络节点
    就像一个微信群，大家都能互相发现
    """
    
    def __init__(self, node_id: str, host: str = "0.0.0.0", port: int = 8000):
        self.node_id = node_id
        self.host = host
        self.port = port
        
        # 已连接的节点（就像微信好友列表）
        self.friends: Dict[str, dict] = {}
        
        # 引导节点（就像群管理员，帮你找到其他人）
        self.bootstrap_nodes = [
            {"host": "bootstrap1.decentralized-ai.network", "port": 8000},
            {"host": "bootstrap2.decentralized-ai.network", "port": 8000}
        ]
        
        self.is_running = False
        
    async def start(self):
        """启动节点 - 就像打开微信"""
        self.is_running = True
        logger.info(f"🚀 节点 {self.node_id} 启动了！地址: {self.host}:{self.port}")
        
        # 启动服务器（开始监听）
        server = await asyncio.start_server(
            self._handle_friend_request, 
            self.host, 
            self.port
        )
        
        logger.info(f"📡 正在监听连接...")
        
        # 连接到引导节点（加入微信群）
        await self._join_network()
        
        async with server:
            await server.serve_forever()
    
    async def _handle_friend_request(self, reader, writer):
        """处理其他节点的连接请求 - 就像有人加你微信"""
        addr = writer.get_extra_info('peername')
        logger.info(f"📨 收到来自 {addr} 的连接")
        
        try:
            while self.is_running:
                # 读取消息
                data = await reader.read(4096)
                if not data:
                    break
                
                # 解析消息
                message = json.loads(data.decode())
                msg_type = message.get('type')
                
                # 处理不同类型的消息
                if msg_type == 'hello':
                    # 新朋友打招呼
                    await self._handle_hello(message, writer)
                    
                elif msg_type == 'discover':
                    # 询问还有哪些朋友
                    await self._handle_discover(writer)
                    
                elif msg_type == 'heartbeat':
                    # 心跳检测（确认朋友还在线）
                    await self._handle_heartbeat(message, writer)
                    
        except Exception as e:
            logger.error(f"❌ 连接出错: {e}")
        finally:
            writer.close()
            await writer.wait_closed()
    
    async def _handle_hello(self, message: dict, writer):
        """处理新朋友的问候"""
        friend_id = message.get('node_id')
        friend_host = message.get('host')
        friend_port = message.get('port')
        
        # 添加到好友列表
        self.friends[friend_id] = {
            'host': friend_host,
            'port': friend_port,
            'connected_at': datetime.now().isoformat(),
            'last_seen': datetime.now().isoformat()
        }
        
        logger.info(f"👋 新朋友加入: {friend_id} ({friend_host}:{friend_port})")
        logger.info(f"📊 当前好友数: {len(self.friends)}")
        
        # 回复问候
        response = {
            'type': 'welcome',
            'node_id': self.node_id,
            'message': f'欢迎 {friend_id}！'
        }
        writer.write(json.dumps(response).encode())
        await writer.drain()
    
    async def _handle_discover(self, writer):
        """告诉对方还有哪些朋友"""
        response = {
            'type': 'peers_list',
            'peers': [
                {
                    'node_id': fid,
                    'host': info['host'],
                    'port': info['port']
                }
                for fid, info in self.friends.items()
            ]
        }
        writer.write(json.dumps(response).encode())
        await writer.drain()
    
    async def _handle_heartbeat(self, message: dict, writer):
        """处理心跳 - 确认朋友还在线"""
        friend_id = message.get('node_id')
        
        if friend_id in self.friends:
            self.friends[friend_id]['last_seen'] = datetime.now().isoformat()
        
        # 回复心跳
        response = {
            'type': 'heartbeat_ack',
            'node_id': self.node_id,
            'timestamp': datetime.now().isoformat()
        }
        writer.write(json.dumps(response).encode())
        await writer.drain()
    
    async def _join_network(self):
        """加入网络 - 就像加入微信群"""
        logger.info("🌐 正在加入网络...")
        
        for bootstrap in self.bootstrap_nodes:
            try:
                await self._connect_to_friend(
                    bootstrap['host'], 
                    bootstrap['port']
                )
            except Exception as e:
                logger.warning(f"⚠️  连接引导节点失败 {bootstrap}: {e}")
        
        # 如果没有引导节点，等待其他节点连接
        if not self.friends:
            logger.info("⏳ 等待其他节点连接...")
    
    async def _connect_to_friend(self, host: str, port: int):
        """连接到其他节点 - 就像加别人微信"""
        try:
            reader, writer = await asyncio.open_connection(host, port)
            
            # 发送问候
            hello_msg = {
                'type': 'hello',
                'node_id': self.node_id,
                'host': self.host,
                'port': self.port
            }
            writer.write(json.dumps(hello_msg).encode())
            await writer.drain()
            
            # 等待欢迎回复
            data = await reader.read(4096)
            response = json.loads(data.decode())
            
            if response.get('type') == 'welcome':
                logger.info(f"✅ 成功连接到: {host}:{port}")
                
                # 询问还有哪些朋友
                writer.write(json.dumps({'type': 'discover'}).encode())
                await writer.drain()
                
                # 读取朋友列表
                data = await reader.read(4096)
                peers_info = json.loads(data.decode())
                
                if peers_info.get('type') == 'peers_list':
                    logger.info(f"📋 发现 {len(peers_info['peers'])} 个其他节点")
                    
                    # 尝试连接这些朋友
                    for peer in peers_info['peers']:
                        if peer['node_id'] != self.node_id:
                            await self._connect_to_friend(
                                peer['host'], 
                                peer['port']
                            )
            
            writer.close()
            await writer.wait_closed()
            
        except Exception as e:
            logger.error(f"❌ 连接失败 {host}:{port}: {e}")
    
    async def send_heartbeat(self):
        """定期发送心跳 - 告诉朋友我还活着"""
        while self.is_running:
            await asyncio.sleep(30)  # 每30秒一次
            
            for friend_id, info in list(self.friends.items()):
                try:
                    reader, writer = await asyncio.open_connection(
                        info['host'], 
                        info['port']
                    )
                    
                    heartbeat_msg = {
                        'type': 'heartbeat',
                        'node_id': self.node_id
                    }
                    writer.write(json.dumps(heartbeat_msg).encode())
                    await writer.drain()
                    
                    writer.close()
                    await writer.wait_closed()
                    
                except Exception as e:
                    logger.warning(f"⚠️  心跳失败 {friend_id}: {e}")
                    # 如果多次失败，可能朋友离线了
    
    def get_status(self) -> dict:
        """获取节点状态"""
        return {
            'node_id': self.node_id,
            'address': f"{self.host}:{self.port}",
            'friends_count': len(self.friends),
            'friends': list(self.friends.keys()),
            'status': 'running' if self.is_running else 'stopped'
        }


# 简单的启动脚本
async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Decentralized AI 节点')
    parser.add_argument('--id', default='node1', help='节点ID')
    parser.add_argument('--port', type=int, default=8000, help='端口号')
    
    args = parser.parse_args()
    
    node = SimpleNode(args.id, port=args.port)
    
    # 同时启动心跳任务
    await asyncio.gather(
        node.start(),
        node.send_heartbeat()
    )


if __name__ == '__main__':
    print("=" * 50)
    print("🚀 Decentralized AI - P2P网络节点")
    print("=" * 50)
    print()
    print("启动示例:")
    print("  python node_step1.py --id mynode --port 8000")
    print()
    print("在另一个终端启动第二个节点:")
    print("  python node_step1.py --id node2 --port 8001")
    print()
    
    asyncio.run(main())
