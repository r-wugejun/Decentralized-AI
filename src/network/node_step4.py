"""
Decentralized AI - 第四步：算力验证机制
防止作弊，确保计算结果正确
"""

import hashlib
import json
import time
import random
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ComputationProof:
    """
    计算证明
    就像考试的答题卡和草稿纸，证明你真的做了计算
    """
    task_id: str
    node_id: str
    input_hash: str        # 输入数据的哈希
    output_hash: str       # 输出结果的哈希
    computation_trace: str # 计算轨迹（简化版）
    timestamp: float
    nonce: int             # 随机数（用于工作量证明）
    
    def to_dict(self) -> dict:
        return {
            'task_id': self.task_id,
            'node_id': self.node_id,
            'input_hash': self.input_hash,
            'output_hash': self.output_hash,
            'computation_trace': self.computation_trace,
            'timestamp': self.timestamp,
            'nonce': self.nonce
        }


class ProofOfComputing:
    """
    算力证明 (Proof of Computing)
    
    核心思想：
    1. 节点提交计算结果 + 证明
    2. 验证者检查证明的有效性
    3. 多个验证者交叉验证
    4. 共识通过后发放奖励
    """
    
    def __init__(self, difficulty: int = 4):
        """
        difficulty: 难度系数，控制验证计算量
        """
        self.difficulty = difficulty
        self.verification_history: Dict[str, List[dict]] = {}
        
    def generate_proof(self, task_id: str, node_id: str, 
                      input_data: Any, output_data: Any) -> ComputationProof:
        """
        生成计算证明
        
        就像做作业时：
        - 记录题目（input_hash）
        - 记录答案（output_hash）
        - 保留草稿（computation_trace）
        - 签名确认（nonce）
        """
        # 计算输入和输出的哈希
        input_str = json.dumps(input_data, sort_keys=True)
        output_str = json.dumps(output_data, sort_keys=True)
        
        input_hash = hashlib.sha256(input_str.encode()).hexdigest()
        output_hash = hashlib.sha256(output_str.encode()).hexdigest()
        
        # 生成计算轨迹（简化版，实际可能包含中间步骤）
        trace = self._generate_computation_trace(input_data, output_data)
        
        # 寻找满足难度要求的nonce（工作量证明）
        nonce = self._find_valid_nonce(task_id, node_id, input_hash, output_hash, trace)
        
        return ComputationProof(
            task_id=task_id,
            node_id=node_id,
            input_hash=input_hash,
            output_hash=output_hash,
            computation_trace=trace,
            timestamp=time.time(),
            nonce=nonce
        )
    
    def _generate_computation_trace(self, input_data: Any, output_data: Any) -> str:
        """生成计算轨迹"""
        # 简化版：记录计算过程的哈希
        # 实际实现中可能包含：
        # - 模型权重哈希
        # - 中间层输出哈希
        # - 随机种子
        trace_data = {
            'input_sample': str(input_data)[:100],  # 输入样本
            'output_sample': str(output_data)[:100],  # 输出样本
            'computation_steps': random.randint(1000, 10000),  # 计算步数
            'memory_usage': random.randint(100, 1000),  # 内存使用(MB)
            'timestamp': datetime.now().isoformat()
        }
        return hashlib.sha256(json.dumps(trace_data).encode()).hexdigest()
    
    def _find_valid_nonce(self, task_id: str, node_id: str, 
                         input_hash: str, output_hash: str, 
                         trace: str) -> int:
        """
        寻找有效的nonce（工作量证明）
        
        就像挖矿：不断尝试，直到找到满足条件的哈希
        """
        target = '0' * self.difficulty
        nonce = 0
        
        while True:
            # 构建待哈希的数据
            data = f"{task_id}{node_id}{input_hash}{output_hash}{trace}{nonce}"
            hash_result = hashlib.sha256(data.encode()).hexdigest()
            
            # 检查是否满足难度要求
            if hash_result.startswith(target):
                return nonce
            
            nonce += 1
            
            # 防止无限循环（实际中应该能很快找到）
            if nonce > 1000000:
                return nonce
    
    def verify_proof(self, proof: ComputationProof, 
                    expected_input: Any, expected_output: Any) -> bool:
        """
        验证计算证明
        
        就像老师批改作业：
        1. 检查题目是否正确（input_hash）
        2. 检查答案是否合理（output_hash）
        3. 检查草稿是否完整（computation_trace）
        4. 检查签名是否有效（nonce）
        """
        # 1. 验证输入哈希
        input_str = json.dumps(expected_input, sort_keys=True)
        expected_input_hash = hashlib.sha256(input_str.encode()).hexdigest()
        if proof.input_hash != expected_input_hash:
            print("❌ 输入数据不匹配")
            return False
        
        # 2. 验证输出哈希（可选，因为输出可能因随机性略有不同）
        # 在实际AI计算中，输出可能因随机种子不同而有差异
        
        # 3. 验证工作量证明
        target = '0' * self.difficulty
        data = f"{proof.task_id}{proof.node_id}{proof.input_hash}{proof.output_hash}{proof.computation_trace}{proof.nonce}"
        hash_result = hashlib.sha256(data.encode()).hexdigest()
        
        if not hash_result.startswith(target):
            print("❌ 工作量证明无效")
            return False
        
        # 4. 验证时间戳（防止重放攻击）
        current_time = time.time()
        if current_time - proof.timestamp > 3600:  # 1小时内有效
            print("❌ 证明已过期")
            return False
        
        print("✅ 证明验证通过")
        return True


class CrossValidator:
    """
    交叉验证器
    
    核心思想：
    - 同一任务分配给多个节点
    - 比较结果的一致性
    - 多数节点的结果被认为是正确的
    """
    
    def __init__(self, min_validators: int = 3, consensus_threshold: float = 0.67):
        """
        min_validators: 最少验证节点数
        consensus_threshold: 共识阈值（如 2/3）
        """
        self.min_validators = min_validators
        self.consensus_threshold = consensus_threshold
        self.results: Dict[str, List[dict]] = {}
        
    def submit_result(self, task_id: str, node_id: str, 
                     result: Any, proof: ComputationProof) -> bool:
        """提交计算结果"""
        if task_id not in self.results:
            self.results[task_id] = []
        
        self.results[task_id].append({
            'node_id': node_id,
            'result': result,
            'proof': proof,
            'timestamp': time.time()
        })
        
        print(f"📨 收到节点 {node_id} 的任务 {task_id} 结果")
        return True
    
    def check_consensus(self, task_id: str) -> Tuple[bool, Any, List[str]]:
        """
        检查是否达成共识
        
        返回：
        - 是否达成共识
        - 共识结果
        - 同意该结果的节点列表
        """
        if task_id not in self.results:
            return False, None, []
        
        submissions = self.results[task_id]
        
        if len(submissions) < self.min_validators:
            print(f"⏳ 等待更多验证... ({len(submissions)}/{self.min_validators})")
            return False, None, []
        
        # 统计结果
        result_votes: Dict[str, List[str]] = {}
        
        for sub in submissions:
            # 将结果转为可哈希的字符串
            result_key = json.dumps(sub['result'], sort_keys=True)
            
            if result_key not in result_votes:
                result_votes[result_key] = []
            result_votes[result_key].append(sub['node_id'])
        
        # 找出得票最多的结果
        total_votes = len(submissions)
        for result_key, voters in result_votes.items():
            vote_ratio = len(voters) / total_votes
            
            if vote_ratio >= self.consensus_threshold:
                consensus_result = json.loads(result_key)
                print(f"✅ 达成共识！{len(voters)}/{total_votes} 节点同意")
                return True, consensus_result, voters
        
        print("❌ 未达成共识")
        return False, None, []


class ReputationSystem:
    """
    声誉系统
    
    核心思想：
    - 记录每个节点的历史表现
    - 诚实节点获得更高声誉
    - 作弊节点被惩罚（降低声誉或封禁）
    """
    
    def __init__(self):
        self.nodes: Dict[str, dict] = {}
        
    def register_node(self, node_id: str):
        """注册新节点"""
        self.nodes[node_id] = {
            'reputation': 50.0,      # 初始声誉 50
            'tasks_completed': 0,
            'tasks_failed': 0,
            'consensus_participations': 0,
            'cheating_detected': 0,
            'joined_at': datetime.now().isoformat()
        }
    
    def record_success(self, node_id: str, task_id: str):
        """记录成功完成任务"""
        if node_id not in self.nodes:
            self.register_node(node_id)
        
        self.nodes[node_id]['tasks_completed'] += 1
        self.nodes[node_id]['consensus_participations'] += 1
        
        # 提升声誉（上限100）
        self.nodes[node_id]['reputation'] = min(
            100, 
            self.nodes[node_id]['reputation'] + 1
        )
        
        print(f"✅ 节点 {node_id} 声誉提升: {self.nodes[node_id]['reputation']}")
    
    def record_failure(self, node_id: str, task_id: str, is_cheating: bool = False):
        """记录任务失败"""
        if node_id not in self.nodes:
            self.register_node(node_id)
        
        self.nodes[node_id]['tasks_failed'] += 1
        
        if is_cheating:
            self.nodes[node_id]['cheating_detected'] += 1
            # 严重惩罚
            self.nodes[node_id]['reputation'] = max(
                0,
                self.nodes[node_id]['reputation'] - 20
            )
            print(f"🚫 节点 {node_id} 检测到作弊！声誉: {self.nodes[node_id]['reputation']}")
        else:
            # 普通失败，轻微惩罚
            self.nodes[node_id]['reputation'] = max(
                0,
                self.nodes[node_id]['reputation'] - 5
            )
            print(f"⚠️  节点 {node_id} 任务失败，声誉: {self.nodes[node_id]['reputation']}")
    
    def get_reputation(self, node_id: str) -> float:
        """获取节点声誉"""
        if node_id not in self.nodes:
            self.register_node(node_id)
        return self.nodes[node_id]['reputation']
    
    def is_trusted(self, node_id: str) -> bool:
        """判断节点是否可信"""
        reputation = self.get_reputation(node_id)
        return reputation >= 30  # 声誉30以上视为可信


class VerificationDemo:
    """验证机制演示"""
    
    @staticmethod
    def run():
        print("=" * 70)
        print("🔐 Decentralized AI - 算力验证机制演示")
        print("=" * 70)
        print()
        
        # 1. 创建算力证明
        print("1️⃣  节点生成计算证明...")
        poc = ProofOfComputing(difficulty=3)
        
        task_id = "task_001"
        node_id = "node_A"
        input_data = {"prompt": "解释量子计算", "max_tokens": 100}
        output_data = {"result": "量子计算是利用量子力学原理..."}
        
        proof = poc.generate_proof(task_id, node_id, input_data, output_data)
        print(f"   ✅ 证明已生成")
        print(f"   - 任务ID: {proof.task_id}")
        print(f"   - 节点ID: {proof.node_id}")
        print(f"   - 工作量证明nonce: {proof.nonce}")
        print()
        
        # 2. 验证证明
        print("2️⃣  验证者验证证明...")
        is_valid = poc.verify_proof(proof, input_data, output_data)
        print()
        
        # 3. 交叉验证
        print("3️⃣  多个节点交叉验证...")
        validator = CrossValidator(min_validators=3)
        
        # 模拟3个节点提交结果
        for i, node in enumerate(['node_A', 'node_B', 'node_C']):
            # 前两个节点结果一致，第三个不同（模拟作弊）
            if i < 2:
                result = output_data
            else:
                result = {"result": "错误的结果..."}  # 作弊节点
            
            proof = poc.generate_proof(task_id, node, input_data, result)
            validator.submit_result(task_id, node, result, proof)
        
        print()
        
        # 4. 检查共识
        print("4️⃣  检查共识结果...")
        consensus, result, voters = validator.check_consensus(task_id)
        
        if consensus:
            print(f"   ✅ 达成共识")
            print(f"   - 同意节点: {voters}")
            print(f"   - 共识结果: {result['result'][:30]}...")
        print()
        
        # 5. 声誉系统
        print("5️⃣  更新节点声誉...")
        reputation = ReputationSystem()
        
        # 注册节点
        for node in ['node_A', 'node_B', 'node_C']:
            reputation.register_node(node)
        
        # 记录结果
        for voter in voters:
            reputation.record_success(voter, task_id)
        
        # 记录作弊节点
        cheater = 'node_C'
        if cheater not in voters:
            reputation.record_failure(cheater, task_id, is_cheating=True)
        
        print()
        print("=" * 70)
        print("✅ 演示完成！")
        print("=" * 70)
        print()
        print("验证机制总结：")
        print("  - 工作量证明：确保节点真的做了计算")
        print("  - 交叉验证：多个节点互相监督")
        print("  - 声誉系统：奖励诚实节点，惩罚作弊者")


if __name__ == '__main__':
    VerificationDemo.run()
