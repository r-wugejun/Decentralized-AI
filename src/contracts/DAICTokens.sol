// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title DAICF Token - 训练算力代币
 * @dev 用于奖励提供训练算力的节点
 * 1份训练算力 = 1份DAICF
 */
contract DAICFToken is ERC20, ERC20Burnable, Ownable {
    
    // 总供应量：无上限（根据实际训练需求发行）
    // 初始供应量：1亿
    uint256 public constant INITIAL_SUPPLY = 100_000_000 * 10**18;
    
    // 奖励池
    uint256 public rewardPool;
    
    // 已发行的训练算力证明（用于计算通胀）
    uint256 public totalTrainingPower;
    
    // 事件
    event TrainingRewardMinted(address indexed provider, uint256 amount, bytes32 taskId);
    event RewardPoolReplenished(uint256 amount);
    
    constructor() ERC20("Decentralized AI Computing - Foundation", "DAICF") {
        _mint(msg.sender, INITIAL_SUPPLY);
        rewardPool = INITIAL_SUPPLY / 2; // 50%用于奖励池
    }
    
    /**
     * @dev 铸造训练奖励
     * 1份训练算力 = 1份DAICF
     */
    function mintTrainingReward(
        address provider, 
        uint256 trainingPower,
        bytes32 taskId
    ) external onlyOwner {
        require(trainingPower > 0, "Invalid training power");
        
        // 1:1 奖励
        uint256 reward = trainingPower;
        
        require(reward <= rewardPool, "Insufficient reward pool");
        
        rewardPool -= reward;
        totalTrainingPower += trainingPower;
        
        _mint(provider, reward);
        
        emit TrainingRewardMinted(provider, reward, taskId);
    }
    
    /**
     * @dev 补充奖励池
     */
    function replenishRewardPool(uint256 amount) external onlyOwner {
        require(balanceOf(msg.sender) >= amount, "Insufficient balance");
        _transfer(msg.sender, address(this), amount);
        rewardPool += amount;
        emit RewardPoolReplenished(amount);
    }
    
    /**
     * @dev 获取奖励池余额
     */
    function getRewardPool() external view returns (uint256) {
        return rewardPool;
    }
    
    /**
     * @dev 获取总训练算力
     */
    function getTotalTrainingPower() external view returns (uint256) {
        return totalTrainingPower;
    }
}

/**
 * @title DAICO Token - 推理算力代币
 * @dev 用于奖励提供推理算力的节点
 * 1份推理算力 = 0.8份给提供者 + 0.2份给DAICF持有者
 */
contract DAICOToken is ERC20, ERC20Burnable, Ownable {
    
    // DAICF 代币合约地址
    address public daicfToken;
    
    // 总供应量：无上限
    uint256 public constant INITIAL_SUPPLY = 100_000_000 * 10**18;
    
    // 奖励分配比例
    uint256 public constant PROVIDER_SHARE = 80;  // 80% 给推理提供者
    uint256 public constant HOLDER_SHARE = 20;    // 20% 给DAICF持有者
    uint256 public constant SHARE_DENOMINATOR = 100;
    
    // 奖励池
    uint256 public rewardPool;
    
    // 已分发给持有者的奖励
    uint256 public totalDistributedToHolders;
    
    // 记录每个DAICF持有者的待领取奖励
    mapping(address => uint256) public pendingHolderRewards;
    
    // 事件
    event InferenceRewardMinted(
        address indexed provider, 
        uint256 providerAmount,
        uint256 holderAmount,
        bytes32 taskId
    );
    event HolderRewardClaimed(address indexed holder, uint256 amount);
    
    constructor(address _daicfToken) ERC20("Decentralized AI Computing - Operation", "DAICO") {
        require(_daicfToken != address(0), "Invalid DAICF address");
        daicfToken = _daicfToken;
        _mint(msg.sender, INITIAL_SUPPLY);
        rewardPool = INITIAL_SUPPLY / 2;
    }
    
    /**
     * @dev 铸造推理奖励
     * 1份推理算力 = 0.8份给提供者 + 0.2份给DAICF持有者
     */
    function mintInferenceReward(
        address provider,
        uint256 inferencePower,
        bytes32 taskId
    ) external onlyOwner {
        require(inferencePower > 0, "Invalid inference power");
        
        // 总奖励 = 推理算力量
        uint256 totalReward = inferencePower;
        require(totalReward <= rewardPool, "Insufficient reward pool");
        
        // 分配给提供者 (80%)
        uint256 providerReward = (totalReward * PROVIDER_SHARE) / SHARE_DENOMINATOR;
        
        // 分配给DAICF持有者 (20%)
        uint256 holderReward = (totalReward * HOLDER_SHARE) / SHARE_DENOMINATOR;
        
        rewardPool -= totalReward;
        
        // 铸造给提供者
        _mint(provider, providerReward);
        
        // 分配给DAICF持有者（按持有比例）
        _distributeToHolders(holderReward);
        
        emit InferenceRewardMinted(provider, providerReward, holderReward, taskId);
    }
    
    /**
     * @dev 分配奖励给DAICF持有者
     */
    function _distributeToHolders(uint256 amount) internal {
        DAICFToken daicf = DAICFToken(daicfToken);
        uint256 totalDaicfSupply = daicf.totalSupply();
        
        if (totalDaicfSupply == 0) {
            // 如果没有DAICF持有者，奖励返回奖励池
            rewardPool += amount;
            return;
        }
        
        // 简化版：记录待分配总额，用户领取时计算
        // 实际实现中可能需要更复杂的机制
        totalDistributedToHolders += amount;
    }
    
    /**
     * @dev 计算并领取持有者奖励
     */
    function claimHolderReward() external {
        DAICFToken daicf = DAICFToken(daicfToken);
        uint256 daicfBalance = daicf.balanceOf(msg.sender);
        uint256 totalDaicfSupply = daicf.totalSupply();
        
        require(daicfBalance > 0, "No DAICF holdings");
        require(totalDaicfSupply > 0, "No DAICF supply");
        
        // 计算应得奖励
        uint256 share = (daicfBalance * 1e18) / totalDaicfSupply;
        uint256 reward = (totalDistributedToHolders * share) / 1e18;
        
        uint256 pending = pendingHolderRewards[msg.sender];
        uint256 totalClaimable = reward - pending;
        
        require(totalClaimable > 0, "No reward to claim");
        
        pendingHolderRewards[msg.sender] = reward;
        _mint(msg.sender, totalClaimable);
        
        emit HolderRewardClaimed(msg.sender, totalClaimable);
    }
    
    /**
     * @dev 查看可领取的奖励
     */
    function getClaimableReward(address holder) external view returns (uint256) {
        DAICFToken daicf = DAICFToken(daicfToken);
        uint256 daicfBalance = daicf.balanceOf(holder);
        uint256 totalDaicfSupply = daicf.totalSupply();
        
        if (daicfBalance == 0 || totalDaicfSupply == 0) {
            return 0;
        }
        
        uint256 share = (daicfBalance * 1e18) / totalDaicfSupply;
        uint256 reward = (totalDistributedToHolders * share) / 1e18;
        uint256 pending = pendingHolderRewards[holder];
        
        return reward > pending ? reward - pending : 0;
    }
    
    /**
     * @dev 补充奖励池
     */
    function replenishRewardPool(uint256 amount) external onlyOwner {
        require(balanceOf(msg.sender) >= amount, "Insufficient balance");
        _transfer(msg.sender, address(this), amount);
        rewardPool += amount;
    }
    
    /**
     * @dev 获取奖励池余额
     */
    function getRewardPool() external view returns (uint256) {
        return rewardPool;
    }
}

/**
 * @title DAIC Reward Manager - 奖励管理合约
 * @dev 统一管理两种代币的奖励发放
 */
contract DAICRewardManager is Ownable {
    
    DAICFToken public daicf;
    DAICOToken public daico;
    
    // 任务记录
    struct TaskReward {
        bytes32 taskId;
        address provider;
        uint256 power;
        bool isTraining;  // true = 训练任务, false = 推理任务
        bool rewarded;
    }
    
    mapping(bytes32 => TaskReward) public taskRewards;
    bytes32[] public taskList;
    
    event TaskRegistered(bytes32 indexed taskId, address provider, uint256 power, bool isTraining);
    event RewardDistributed(bytes32 indexed taskId, uint256 amount);
    
    constructor(address _daicf, address _daico) {
        daicf = DAICFToken(_daicf);
        daico = DAICOToken(_daico);
    }
    
    /**
     * @dev 注册训练任务
     */
    function registerTrainingTask(
        bytes32 taskId,
        address provider,
        uint256 trainingPower
    ) external onlyOwner {
        require(taskRewards[taskId].provider == address(0), "Task already registered");
        
        taskRewards[taskId] = TaskReward({
            taskId: taskId,
            provider: provider,
            power: trainingPower,
            isTraining: true,
            rewarded: false
        });
        taskList.push(taskId);
        
        emit TaskRegistered(taskId, provider, trainingPower, true);
    }
    
    /**
     * @dev 注册推理任务
     */
    function registerInferenceTask(
        bytes32 taskId,
        address provider,
        uint256 inferencePower
    ) external onlyOwner {
        require(taskRewards[taskId].provider == address(0), "Task already registered");
        
        taskRewards[taskId] = TaskReward({
            taskId: taskId,
            provider: provider,
            power: inferencePower,
            isTraining: false,
            rewarded: false
        });
        taskList.push(taskId);
        
        emit TaskRegistered(taskId, provider, inferencePower, false);
    }
    
    /**
     * @dev 发放奖励
     */
    function distributeReward(bytes32 taskId) external onlyOwner {
        TaskReward storage task = taskRewards[taskId];
        require(task.provider != address(0), "Task not found");
        require(!task.rewarded, "Already rewarded");
        
        if (task.isTraining) {
            // 发放DAICF奖励（1:1）
            daicf.mintTrainingReward(task.provider, task.power, taskId);
        } else {
            // 发放DAICO奖励（0.8 + 0.2）
            daico.mintInferenceReward(task.provider, task.power, taskId);
        }
        
        task.rewarded = true;
        emit RewardDistributed(taskId, task.power);
    }
    
    /**
     * @dev 批量发放奖励
     */
    function batchDistributeRewards(bytes32[] calldata taskIds) external onlyOwner {
        for (uint i = 0; i < taskIds.length; i++) {
            this.distributeReward(taskIds[i]);
        }
    }
    
    /**
     * @dev 获取任务数量
     */
    function getTaskCount() external view returns (uint256) {
        return taskList.length;
    }
}
