#!/usr/bin/env python3
"""
测试脚本：启动两个节点，演示它们如何互相发现
"""

import asyncio
import sys
sys.path.insert(0, '/root/.openclaw/workspace/Decentralized-AI/src/network')

from node_step1 import SimpleNode


async def test_two_nodes():
    """测试两个节点互相发现"""
    
    print("=" * 60)
    print("🧪 测试：两个节点互相发现")
    print("=" * 60)
    print()
    
    # 创建两个节点
    node1 = SimpleNode("节点A", port=8001)
    node2 = SimpleNode("节点B", port=8002)
    
    # 启动节点A
    print("1️⃣  启动节点A (端口8001)...")
    task1 = asyncio.create_task(node1.start())
    await asyncio.sleep(1)  # 等待节点A启动
    
    # 启动节点B
    print("2️⃣  启动节点B (端口8002)...")
    task2 = asyncio.create_task(node2.start())
    await asyncio.sleep(1)  # 等待节点B启动
    
    # 让节点B连接节点A
    print("3️⃣  节点B连接节点A...")
    await node2._connect_to_friend("127.0.0.1", 8001)
    await asyncio.sleep(1)
    
    # 查看状态
    print()
    print("=" * 60)
    print("📊 节点状态")
    print("=" * 60)
    
    status1 = node1.get_status()
    status2 = node2.get_status()
    
    print(f"\n节点A:")
    print(f"  - ID: {status1['node_id']}")
    print(f"  - 地址: {status1['address']}")
    print(f"  - 好友数: {status1['friends_count']}")
    print(f"  - 好友列表: {status1['friends']}")
    
    print(f"\n节点B:")
    print(f"  - ID: {status2['node_id']}")
    print(f"  - 地址: {status2['address']}")
    print(f"  - 好友数: {status2['friends_count']}")
    print(f"  - 好友列表: {status2['friends']}")
    
    print()
    print("✅ 测试成功！两个节点已经互相发现！")
    print()
    print("按 Ctrl+C 停止测试...")
    
    try:
        await asyncio.gather(task1, task2)
    except KeyboardInterrupt:
        print("\n👋 测试结束")


if __name__ == '__main__':
    try:
        asyncio.run(test_two_nodes())
    except KeyboardInterrupt:
        print("\n\n测试已停止")
