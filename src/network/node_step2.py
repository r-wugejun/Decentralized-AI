"""
Decentralized AI - 第二步：任务分配协议
支持两种算力类型：训练算力 + 推理算力
"""

import asyncio
import json
import logging
import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskType(Enum):
    """任务类型"""
    TRAINING = "training"      # 训练任务 - 构建大模型
    INFERENCE = "inference"    # 推理任务 - 运行大模型


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"        # 等待分配
    ASSIGNED = "assigned"      # 已分配
    RUNNING = "running"        # 运行中
    COMPLETED = "completed"    # 已完成
    FAILED = "failed"          # 失败


@dataclass
class Task:
    """
    任务定义
    
    训练任务示例：
    - 类型：TRAINING
    - 数据：大量文本数据
    - 计算：需要GPU，长时间运行
    - 结果：模型权重文件
    
    推理任务示例：
    - 类型：INFERENCE
    - 数据：用户输入的问题
    - 计算：快速响应，单次前向传播
    - 结果：AI生成的回答
    """
    task_id: str
    task_type: TaskType
    status: TaskStatus
    
    # 任务内容
    model_name: str           # 模型名称（如 "grok-like-7b"）
    data: Any                 # 输入数据
    parameters: Dict          # 任务参数
    
    # 资源需求
    required_gpu: bool        # 是否需要GPU
    required_memory: int      # 需要内存（GB）
    estimated_time: int       # 预计时间（秒）
    
    # 任务元信息
    created_at: str
    assigned_to: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result: Optional[Any] = None
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'task_id': self.task_id,
            'task_type': self.task_type.value,
            'status': self.status.value,
            'model_name': self.model_name,
            'data': self.data,
            'parameters': self.parameters,
            'required_gpu': self.required_gpu,
            'required_memory': self.required_memory,
            'estimated_time': self.estimated_time,
            'created_at': self.created_at,
            'assigned_to': self.assigned_to,
            'started_at': self.started_at,
            'completed_at': self.completed_at,
            'result': self.result
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Task':
        """从字典创建"""
        return cls(
            task_id=data['task_id'],
            task_type=TaskType(data['task_type']),
            status=TaskStatus(data['status']),
            model_name=data['model_name'],
            data=data['data'],
            parameters=data['parameters'],
            required_gpu=data['required_gpu'],
            required_memory=data['required_memory'],
            estimated_time=data['estimated_time'],
            created_at=data['created_at'],
            assigned_to=data.get('assigned_to'),
            started_at=data.get('started_at'),
            completed_at=data.get('completed_at'),
            result=data.get('result')
        )


class TaskScheduler:
    """
    任务调度器
    
    就像外卖平台：
    - 用户下单（提交任务）
    - 平台分配（调度器找合适的骑手/算力节点）
    - 骑手配送（节点执行任务）
    - 确认完成（返回结果）
    """
    
    def __init__(self):
        # 任务队列
        self.training_queue: List[Task] = []    # 训练任务队列
        self.inference_queue: List[Task] = []   # 推理任务队列
        
        # 进行中的任务
        self.running_tasks: Dict[str, Task] = {}
        
        # 完成的任务
        self.completed_tasks: Dict[str, Task] = {}
        
        # 可用的算力节点
        self.available_workers: Dict[str, dict] = {}
        
    def submit_training_task(
        self,
        model_name: str,
        dataset: str,           # 数据集名称或路径
        hyperparameters: dict,   # 超参数
        required_gpu: bool = True,
        required_memory: int = 16   # GB
    ) -> str:
        """
        提交训练任务
        
        示例：
        task_id = scheduler.submit_training_task(
            model_name="grok-like-7b",
            dataset="common_crawl_2024",
            hyperparameters={
                "epochs": 3,
                "batch_size": 32,
                "learning_rate": 1e-4
            }
        )
        """
        task = Task(
            task_id=str(uuid.uuid4()),
            task_type=TaskType.TRAINING,
            status=TaskStatus.PENDING,
            model_name=model_name,
            data={"dataset": dataset},
            parameters=hyperparameters,
            required_gpu=required_gpu,
            required_memory=required_memory,
            estimated_time=86400,  # 预计24小时
            created_at=datetime.now().isoformat()
        )
        
        self.training_queue.append(task)
        logger.info(f"📝 训练任务已提交: {task.task_id[:8]}... 模型: {model_name}")
        
        return task.task_id
    
    def submit_inference_task(
        self,
        model_name: str,
        prompt: str,            # 用户输入
        max_tokens: int = 512,   # 最大生成token数
        temperature: float = 0.7
    ) -> str:
        """
        提交推理任务
        
        示例：
        task_id = scheduler.submit_inference_task(
            model_name="grok-like-7b",
            prompt="解释量子计算",
            max_tokens=256
        )
        """
        task = Task(
            task_id=str(uuid.uuid4()),
            task_type=TaskType.INFERENCE,
            status=TaskStatus.PENDING,
            model_name=model_name,
            data={"prompt": prompt},
            parameters={
                "max_tokens": max_tokens,
                "temperature": temperature
            },
            required_gpu=True,
            required_memory=8,   # 推理需要较少内存
            estimated_time=5,    # 预计5秒
            created_at=datetime.now().isoformat()
        )
        
        self.inference_queue.append(task)
        logger.info(f"💬 推理任务已提交: {task.task_id[:8]}... 提示: {prompt[:30]}...")
        
        return task.task_id
    
    def register_worker(self, worker_id: str, capabilities: dict):
        """
        注册算力节点
        
        capabilities = {
            "has_gpu": True,
            "gpu_memory": 24,        # GB
            "cpu_cores": 16,
            "memory": 64,            # GB
            "bandwidth": 1000,       # Mbps
            "location": "上海"
        }
        """
        self.available_workers[worker_id] = {
            **capabilities,
            "status": "idle",
            "registered_at": datetime.now().isoformat()
        }
        logger.info(f"👷 算力节点注册: {worker_id}")
    
    def find_best_worker(self, task: Task) -> Optional[str]:
        """
        找到最适合执行任务的节点
        
        策略：
        1. 训练任务 → 找GPU强、稳定的节点
        2. 推理任务 → 找延迟低、响应快的节点
        """
        suitable_workers = []
        
        for worker_id, caps in self.available_workers.items():
            # 检查基本要求
            if task.required_gpu and not caps.get("has_gpu"):
                continue
            if caps.get("memory", 0) < task.required_memory:
                continue
            if caps.get("status") != "idle":
                continue
            
            # 计算匹配分数
            score = 0
            
            if task.task_type == TaskType.TRAINING:
                # 训练任务：优先GPU强、稳定的节点
                score += caps.get("gpu_memory", 0) * 10
                score += caps.get("memory", 0)
                # 信誉加成（假设有信誉系统）
                score += caps.get("reputation", 50)
                
            elif task.task_type == TaskType.INFERENCE:
                # 推理任务：优先延迟低、响应快的节点
                score += 1000 / (caps.get("latency", 100) + 1)
                score += caps.get("bandwidth", 100) / 10
            
            suitable_workers.append((worker_id, score))
        
        if not suitable_workers:
            return None
        
        # 选择分数最高的
        suitable_workers.sort(key=lambda x: x[1], reverse=True)
        return suitable_workers[0][0]
    
    async def schedule_tasks(self):
        """
        调度任务
        不断检查队列，分配任务给合适的节点
        """
        while True:
            # 优先处理推理任务（实时性要求高）
            if self.inference_queue:
                task = self.inference_queue.pop(0)
                worker_id = self.find_best_worker(task)
                
                if worker_id:
                    await self.assign_task(task, worker_id)
                else:
                    # 没有可用节点，放回队列
                    self.inference_queue.insert(0, task)
            
            # 处理训练任务
            if self.training_queue:
                task = self.training_queue.pop(0)
                worker_id = self.find_best_worker(task)
                
                if worker_id:
                    await self.assign_task(task, worker_id)
                else:
                    self.training_queue.insert(0, task)
            
            await asyncio.sleep(1)  # 每秒检查一次
    
    async def assign_task(self, task: Task, worker_id: str):
        """分配任务给节点"""
        task.status = TaskStatus.ASSIGNED
        task.assigned_to = worker_id
        task.started_at = datetime.now().isoformat()
        
        self.running_tasks[task.task_id] = task
        self.available_workers[worker_id]["status"] = "busy"
        
        logger.info(f"🚀 任务 {task.task_id[:8]}... 分配给节点 {worker_id}")
        
        # 这里会通过网络发送任务给worker节点
        # 实际实现中需要调用P2P网络发送
    
    def complete_task(self, task_id: str, result: Any):
        """任务完成"""
        if task_id in self.running_tasks:
            task = self.running_tasks.pop(task_id)
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now().isoformat()
            task.result = result
            
            self.completed_tasks[task_id] = task
            
            # 释放worker
            if task.assigned_to:
                self.available_workers[task.assigned_to]["status"] = "idle"
            
            logger.info(f"✅ 任务完成: {task_id[:8]}...")
    
    def get_task_status(self, task_id: str) -> Optional[dict]:
        """查询任务状态"""
        # 在队列中查找
        for task in self.training_queue + self.inference_queue:
            if task.task_id == task_id:
                return task.to_dict()
        
        # 在运行中查找
        if task_id in self.running_tasks:
            return self.running_tasks[task_id].to_dict()
        
        # 在已完成中查找
        if task_id in self.completed_tasks:
            return self.completed_tasks[task_id].to_dict()
        
        return None
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        return {
            "training_pending": len(self.training_queue),
            "inference_pending": len(self.inference_queue),
            "running": len(self.running_tasks),
            "completed": len(self.completed_tasks),
            "available_workers": len([w for w in self.available_workers.values() if w["status"] == "idle"])
        }


# 使用示例
async def demo():
    """演示如何使用任务调度器"""
    
    scheduler = TaskScheduler()
    
    # 注册一些算力节点
    scheduler.register_worker("worker_gpu_1", {
        "has_gpu": True,
        "gpu_memory": 24,
        "memory": 64,
        "bandwidth": 1000,
        "reputation": 95
    })
    
    scheduler.register_worker("worker_gpu_2", {
        "has_gpu": True,
        "gpu_memory": 48,
        "memory": 128,
        "bandwidth": 500,
        "reputation": 90
    })
    
    scheduler.register_worker("worker_edge_1", {
        "has_gpu": False,
        "memory": 16,
        "bandwidth": 100,
        "latency": 20
    })
    
    print("=" * 60)
    print("🚀 Decentralized AI - 任务调度演示")
    print("=" * 60)
    print()
    
    # 提交训练任务
    print("1️⃣  提交训练任务（构建大模型）...")
    training_task = scheduler.submit_training_task(
        model_name="grok-like-7b",
        dataset="common_crawl_2024",
        hyperparameters={"epochs": 3, "batch_size": 32}
    )
    print(f"   任务ID: {training_task[:8]}...")
    print()
    
    # 提交推理任务
    print("2️⃣  提交推理任务（运行大模型）...")
    inference_task = scheduler.submit_inference_task(
        model_name="grok-like-7b",
        prompt="解释量子计算的原理",
        max_tokens=256
    )
    print(f"   任务ID: {inference_task[:8]}...")
    print()
    
    # 显示统计
    print("3️⃣  当前状态统计:")
    stats = scheduler.get_stats()
    print(f"   - 训练任务排队: {stats['training_pending']}")
    print(f"   - 推理任务排队: {stats['inference_pending']}")
    print(f"   - 可用算力节点: {stats['available_workers']}")
    print()
    
    print("✅ 演示完成！")
    print()
    print("说明：")
    print("  - 训练任务：需要长时间运行，构建AI大模型")
    print("  - 推理任务：快速响应，为用户提供AI服务")


if __name__ == '__main__':
    asyncio.run(demo())
