"""
第二步完成：任务分配协议

通俗解释：
=========
就像外卖平台：
- 用户下单 = 提交AI任务
- 平台派单 = 调度器找合适的算力节点
- 骑手配送 = 节点执行计算
- 确认完成 = 返回AI结果

两种任务类型：
==============

1. 训练任务 (TRAINING)
   用途：构建类似 Grok 的大模型
   特点：
   - 需要长时间运行（几小时到几天）
   - 需要强大的GPU
   - 处理大量数据
   - 结果是模型权重文件
   
   示例：
   - 训练一个70亿参数的模型
   - 使用全网爬取的数据
   - 运行3个epoch

2. 推理任务 (INFERENCE)
   用途：给大模型运行提供算力支持
   特点：
   - 实时响应（几秒钟）
   - 单次计算量小
   - 需要低延迟
   - 结果是AI生成的回答
   
   示例：
   - 用户问："解释量子计算"
   - AI生成回答
   - 快速返回给用户

调度策略：
=========

训练任务 → 找GPU强、稳定的节点
推理任务 → 找延迟低、响应快的节点

核心功能：
=========

1. submit_training_task() - 提交训练任务
2. submit_inference_task() - 提交推理任务
3. register_worker() - 注册算力节点
4. find_best_worker() - 智能匹配节点
5. schedule_tasks() - 自动调度任务

使用方法：
=========

# 创建调度器
scheduler = TaskScheduler()

# 注册算力节点
scheduler.register_worker("gpu_node_1", {
    "has_gpu": True,
    "gpu_memory": 24,
    "memory": 64
})

# 提交训练任务
task_id = scheduler.submit_training_task(
    model_name="grok-like-7b",
    dataset="training_data",
    hyperparameters={"epochs": 3}
)

# 提交推理任务
task_id = scheduler.submit_inference_task(
    model_name="grok-like-7b",
    prompt="你好，AI"
)

# 查询任务状态
status = scheduler.get_task_status(task_id)

下一步：
=======

第三步：开发轻量级客户端
让用户一键参与，后台运行不影响正常使用
"""

print(__doc__)
