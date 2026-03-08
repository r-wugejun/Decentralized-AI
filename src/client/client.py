"""
Decentralized AI - 第三步：轻量级客户端
一键参与，后台运行，不影响正常使用
"""

import asyncio
import json
import logging
import os
import sys
import time
import threading
from typing import Dict, Optional
from datetime import datetime
from dataclasses import dataclass
import psutil

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('decentralized_ai.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class ClientConfig:
    """客户端配置"""
    node_id: str
    max_cpu_percent: int = 50      # 最大CPU使用率
    max_memory_percent: int = 30   # 最大内存使用率
    max_gpu_percent: int = 60      # 最大GPU使用率
    idle_threshold: int = 30       # 空闲判断阈值（秒）
    auto_start: bool = True        # 开机自启
    

class ResourceMonitor:
    """
    资源监控器
    像智能管家一样，时刻关注电脑使用情况
    """
    
    def __init__(self, config: ClientConfig):
        self.config = config
        self.is_idle = True
        self.idle_start_time = time.time()
        
    def check_resources(self) -> Dict:
        """检查当前资源使用情况"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        # 检查GPU（如果有）
        gpu_info = self._check_gpu()
        
        return {
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'memory_available_gb': memory.available / (1024**3),
            'gpu_percent': gpu_info.get('percent', 0),
            'gpu_memory_percent': gpu_info.get('memory_percent', 0),
            'is_idle': self._is_system_idle(cpu_percent, memory.percent)
        }
    
    def _check_gpu(self) -> Dict:
        """检查GPU使用情况"""
        try:
            # 尝试使用 nvidia-ml-py
            import pynvml
            pynvml.nvmlInit()
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            util = pynvml.nvmlDeviceGetUtilizationRates(handle)
            mem = pynvml.nvmlDeviceGetMemoryInfo(handle)
            
            return {
                'percent': util.gpu,
                'memory_percent': (mem.used / mem.total) * 100
            }
        except:
            # 没有NVIDIA GPU或驱动
            return {'percent': 0, 'memory_percent': 0}
    
    def _is_system_idle(self, cpu: float, memory: float) -> bool:
        """判断系统是否空闲"""
        # 如果CPU和内存使用都低于阈值，认为是空闲
        if cpu < self.config.max_cpu_percent and memory < self.config.max_memory_percent:
            if not self.is_idle:
                self.is_idle = True
                self.idle_start_time = time.time()
        else:
            self.is_idle = False
            self.idle_start_time = time.time()
        
        # 需要持续空闲一段时间才真正开始工作
        if self.is_idle:
            idle_duration = time.time() - self.idle_start_time
            return idle_duration >= self.config.idle_threshold
        
        return False


class LightweightClient:
    """
    轻量级客户端
    就像后台运行的音乐播放器，不影响你正常使用电脑
    """
    
    def __init__(self, config: ClientConfig):
        self.config = config
        self.monitor = ResourceMonitor(config)
        self.is_running = False
        self.current_task = None
        self.stats = {
            'tasks_completed': 0,
            'compute_time': 0,
            'earnings_daicf': 0.0,
            'earnings_daico': 0.0
        }
        
    def start(self):
        """启动客户端"""
        logger.info("=" * 60)
        logger.info("🚀 Decentralized AI 客户端启动")
        logger.info("=" * 60)
        logger.info(f"节点ID: {self.config.node_id}")
        logger.info(f"CPU限制: {self.config.max_cpu_percent}%")
        logger.info(f"内存限制: {self.config.max_memory_percent}%")
        logger.info(f"GPU限制: {self.config.max_gpu_percent}%")
        logger.info("=" * 60)
        
        self.is_running = True
        
        # 启动后台线程
        threading.Thread(target=self._main_loop, daemon=True).start()
        
        logger.info("✅ 客户端已在后台运行")
        logger.info("💡 提示：你可以正常使用电脑，客户端会在空闲时自动工作")
        
    def _main_loop(self):
        """主循环"""
        while self.is_running:
            try:
                # 检查资源
                resources = self.monitor.check_resources()
                
                if resources['is_idle']:
                    # 系统空闲，开始工作
                    if not self.current_task:
                        self._start_computing()
                else:
                    # 系统忙碌，暂停工作
                    if self.current_task:
                        self._pause_computing()
                
                # 每秒检查一次
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"主循环错误: {e}")
                time.sleep(5)
    
    def _start_computing(self):
        """开始计算"""
        logger.info("💻 系统空闲，开始提供算力...")
        
        # 这里会连接到网络，获取任务
        # 简化版：模拟执行任务
        self.current_task = {
            'start_time': time.time(),
            'type': 'training'  # 或 'inference'
        }
        
        # 实际实现中，这里会：
        # 1. 连接到P2P网络
        # 2. 向调度器注册
        # 3. 获取任务
        # 4. 执行计算
        # 5. 返回结果
        
        threading.Thread(target=self._execute_task, daemon=True).start()
    
    def _pause_computing(self):
        """暂停计算"""
        logger.info("⏸️  检测到系统忙碌，暂停算力提供...")
        self.current_task = None
    
    def _execute_task(self):
        """执行任务（模拟）"""
        while self.current_task and self.is_running:
            # 检查是否仍然空闲
            resources = self.monitor.check_resources()
            if not resources['is_idle']:
                break
            
            # 模拟计算工作
            time.sleep(1)
            self.stats['compute_time'] += 1
            
            # 每60秒记录一次收益（模拟）
            if self.stats['compute_time'] % 60 == 0:
                self._record_earnings()
        
        if self.current_task:
            self.stats['tasks_completed'] += 1
            self.current_task = None
            logger.info(f"✅ 任务完成！已完成 {self.stats['tasks_completed']} 个任务")
    
    def _record_earnings(self):
        """记录收益"""
        # 模拟收益计算
        # 实际会根据完成的任务类型和算力贡献计算
        if self.current_task and self.current_task['type'] == 'training':
            self.stats['earnings_daicf'] += 0.1
        else:
            self.stats['earnings_daico'] += 0.08
    
    def get_status(self) -> Dict:
        """获取客户端状态"""
        resources = self.monitor.check_resources()
        
        return {
            'node_id': self.config.node_id,
            'is_running': self.is_running,
            'is_working': self.current_task is not None,
            'system_idle': resources['is_idle'],
            'cpu_usage': resources['cpu_percent'],
            'memory_usage': resources['memory_percent'],
            'stats': self.stats
        }
    
    def stop(self):
        """停止客户端"""
        logger.info("🛑 正在停止客户端...")
        self.is_running = False
        self.current_task = None
        logger.info("👋 客户端已停止")


class OneClickInstaller:
    """
    一键安装器
    让安装像安装微信一样简单
    """
    
    @staticmethod
    def install():
        """安装客户端"""
        print("=" * 60)
        print("🚀 Decentralized AI 客户端安装")
        print("=" * 60)
        print()
        
        # 检查系统要求
        print("1️⃣  检查系统要求...")
        if not OneClickInstaller._check_requirements():
            print("❌ 系统不满足最低要求")
            return False
        print("✅ 系统检查通过")
        print()
        
        # 创建配置
        print("2️⃣  创建配置文件...")
        node_id = OneClickInstaller._generate_node_id()
        config = ClientConfig(node_id=node_id)
        OneClickInstaller._save_config(config)
        print(f"✅ 节点ID: {node_id}")
        print()
        
        # 创建启动脚本
        print("3️⃣  创建启动脚本...")
        OneClickInstaller._create_startup_scripts()
        print("✅ 启动脚本已创建")
        print()
        
        print("=" * 60)
        print("🎉 安装完成！")
        print("=" * 60)
        print()
        print("使用方法：")
        print("  启动: python client.py start")
        print("  停止: python client.py stop")
        print("  状态: python client.py status")
        print()
        print("或者双击 start.bat (Windows) 或 start.sh (Mac/Linux)")
        print()
        
        return True
    
    @staticmethod
    def _check_requirements():
        """检查系统要求"""
        # 检查Python版本
        if sys.version_info < (3, 8):
            print("❌ 需要Python 3.8或更高版本")
            return False
        
        # 检查内存
        memory = psutil.virtual_memory()
        if memory.total < 4 * 1024**3:  # 4GB
            print("⚠️  内存小于4GB，可能影响性能")
        
        return True
    
    @staticmethod
    def _generate_node_id():
        """生成节点ID"""
        import uuid
        return f"node_{uuid.uuid4().hex[:8]}"
    
    @staticmethod
    def _save_config(config: ClientConfig):
        """保存配置"""
        config_data = {
            'node_id': config.node_id,
            'max_cpu_percent': config.max_cpu_percent,
            'max_memory_percent': config.max_memory_percent,
            'max_gpu_percent': config.max_gpu_percent,
            'idle_threshold': config.idle_threshold,
            'auto_start': config.auto_start
        }
        
        with open('config.json', 'w') as f:
            json.dump(config_data, f, indent=2)
    
    @staticmethod
    def _create_startup_scripts():
        """创建启动脚本"""
        # Windows批处理脚本
        with open('start.bat', 'w') as f:
            f.write('@echo off\n')
            f.write('echo Starting Decentralized AI Client...\n')
            f.write('python client.py start\n')
            f.write('pause\n')
        
        # Linux/Mac shell脚本
        with open('start.sh', 'w') as f:
            f.write('#!/bin/bash\n')
            f.write('echo "Starting Decentralized AI Client..."\n')
            f.write('python3 client.py start\n')
        
        os.chmod('start.sh', 0o755)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Decentralized AI 轻量级客户端')
    parser.add_argument('command', choices=['install', 'start', 'stop', 'status'], 
                       help='命令: install(安装), start(启动), stop(停止), status(状态)')
    
    args = parser.parse_args()
    
    if args.command == 'install':
        OneClickInstaller.install()
    
    elif args.command == 'start':
        # 加载配置
        if not os.path.exists('config.json'):
            print("❌ 未找到配置文件，请先运行: python client.py install")
            return
        
        with open('config.json', 'r') as f:
            config_data = json.load(f)
        
        config = ClientConfig(**config_data)
        client = LightweightClient(config)
        client.start()
        
        # 保持运行
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            client.stop()
    
    elif args.command == 'stop':
        print("🛑 发送停止信号...")
        # 实际实现中需要进程间通信
    
    elif args.command == 'status':
        # 显示状态
        print("📊 客户端状态")
        print("=" * 40)
        # 实际实现中从日志或状态文件读取


if __name__ == '__main__':
    print("""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║           Decentralized AI - 轻量级客户端                 ║
║                                                          ║
║   一键参与，后台运行，不影响正常使用                      ║
║   提供闲置算力，赚取 DAICF/DAICO 代币                     ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    print("使用方法:")
    print("  1. 安装:   python client.py install")
    print("  2. 启动:   python client.py start")
    print("  3. 停止:   python client.py stop")
    print("  4. 状态:   python client.py status")
    print()
    
    main()
