"""
Decentralized AI - 多设备算力支持策略

## 设备分级体系

### Tier 1: 高性能设备 (PC/工作站/云服务器)
- 算力: > 10 TFLOPS
- 适用: 训练任务 + 推理任务
- 奖励: 100% (1:1 DAICF/DAICO)

### Tier 2: 中性能设备 (高端手机/平板)
- 算力: 1-10 TFLOPS  
- 适用: 轻量推理任务
- 奖励: 50% (0.5:1 DAICF/DAICO)

### Tier 3: 低性能设备 (普通手机/IoT)
- 算力: < 1 TFLOPS
- 适用: 数据预处理、联邦学习聚合
- 奖励: 20% (0.2:1 DAICF/DAICO)

## 设备适配策略

### PC/云服务器 (当前已实现)
- Python客户端
- 完整功能支持
- GPU加速

### Android (第二阶段开发)
- Kotlin/Java 或 Flutter
- TensorFlow Lite
- 只在充电时运行
- WiFi优先（省流量）

### iOS (第三阶段)
- Swift 开发
- Core ML 框架
- 需要用户主动参与模式

## 任务分级

### 训练任务 (仅Tier 1)
- 大模型训练
- 需要GPU显存 > 8GB
- 长时间运行

### 标准推理 (Tier 1 + Tier 2)
- 中等规模模型
- 响应时间 < 1秒
- 需要NPU/GPU

### 轻量推理 (所有Tier)
- 小型模型
- 文本分类、简单识别
- CPU即可运行

## 经济模型调整

### 多设备奖励公式

```python
def calculate_reward(device_tier, compute_power, task_type):
    base_reward = compute_power
    
    # 设备等级系数
    tier_multiplier = {
        1: 1.0,    # PC/云
        2: 0.5,    # 高端手机
        3: 0.2     # 普通手机
    }
    
    # 任务类型系数
    task_multiplier = {
        'training': 1.0,
        'inference_standard': 0.8,
        'inference_light': 0.3
    }
    
    reward = base_reward * tier_multiplier[device_tier] * task_multiplier[task_type]
    return reward
```

### 示例

| 设备 | 任务 | 算力 | 基础奖励 | 实际奖励 |
|------|------|------|---------|---------|
| RTX 4090 | 训练 | 100 | 100 DAICF | 100 DAICF |
| 云服务器 | 推理 | 50 | 50 DAICO | 40 DAICO |
| iPhone 15 | 轻量推理 | 10 | 10 DAICO | 3 DAICO |
| 安卓旗舰 | 轻量推理 | 5 | 5 DAICO | 1.5 DAICO |

## 开发优先级

### 当前 (Phase 1)
✅ PC客户端 (Windows/Mac/Linux)
✅ 云服务器支持

### 下一阶段 (Phase 2)
🔄 Android客户端
🔄 任务分级系统
🔄 设备检测自动分级

### 未来 (Phase 3)
⏳ iOS客户端（有限支持）
⏳ IoT设备支持
⏳ 边缘计算优化

## 用户场景

### 场景1：游戏玩家
设备：RTX 4080游戏PC
参与：挂机时提供训练算力
收益：每天 50-100 DAICF

### 场景2：手机用户
设备：骁龙8 Gen3安卓旗舰
参与：充电时提供轻量推理
收益：每天 5-10 DAICO

### 场景3：云服务商
设备：A100云服务器
参与：24/7提供稳定算力
收益：每天 500+ DAICF/DAICO

### 场景4：普通用户
设备：办公笔记本
参与：午休/下班时运行
收益：每天 10-20 DAICF

## 结论

**当前专注：PC + 云服务器**
- 技术成熟
- 算力质量高
- 开发成本低

**未来扩展：安卓手机**
- 数量庞大
- 适合轻量任务
- 需要解决电池/散热问题

**暂不推荐：苹果设备**
- 生态限制太多
- 开发成本高
- 用户获取困难
"""

print(__doc__)
