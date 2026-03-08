// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title DAIC Token
 * @dev Decentralized AI Computing Token
 */
contract DAICToken is ERC20, ERC20Burnable, Ownable {
    
    // 代币分配
    uint256 public constant TOTAL_SUPPLY = 1_000_000_000 * 10**18; // 10亿
    
    // 分配比例
    uint256 public constant MINING_REWARD = 500_000_000 * 10**18;  // 50%
    uint256 public constant TEAM_ALLOCATION = 200_000_000 * 10**18; // 20%
    uint256 public constant ECOSYSTEM = 150_000_000 * 10**18;       // 15%
    uint256 public constant INVESTORS = 100_000_000 * 10**18;       // 10%
    uint256 public constant AIRDROP = 50_000_000 * 10**18;          // 5%
    
    // 挖矿相关
    uint256 public miningRewardPerBlock;
    uint256 public lastHalvingBlock;
    uint256 public constant HALVING_PERIOD = 2 * 365 * 24 * 60 * 60 / 12; // 约2年 (按12秒出块)
    
    // 质押相关
    mapping(address => uint256) public stakes;
    mapping(address => uint256) public stakeTime;
    uint256 public totalStaked;
    uint256 public constant MIN_STAKE = 1000 * 10**18; // 最小质押1000 DAIC
    
    // 事件
    event Stake(address indexed user, uint256 amount);
    event Unstake(address indexed user, uint256 amount);
    event RewardDistributed(address indexed user, uint256 amount);
    
    constructor() ERC20("Decentralized AI Computing", "DAIC") {
        _mint(msg.sender, TOTAL_SUPPLY);
        miningRewardPerBlock = 100 * 10**18; // 初始每区块奖励100 DAIC
        lastHalvingBlock = block.number;
    }
    
    /**
     * @dev 质押代币
     */
    function stake(uint256 amount) external {
        require(amount >= MIN_STAKE, "Stake amount too low");
        require(balanceOf(msg.sender) >= amount, "Insufficient balance");
        
        _transfer(msg.sender, address(this), amount);
        stakes[msg.sender] += amount;
        stakeTime[msg.sender] = block.timestamp;
        totalStaked += amount;
        
        emit Stake(msg.sender, amount);
    }
    
    /**
     * @dev 解除质押
     */
    function unstake(uint256 amount) external {
        require(stakes[msg.sender] >= amount, "Insufficient stake");
        require(block.timestamp >= stakeTime[msg.sender] + 7 days, "Stake locked for 7 days");
        
        stakes[msg.sender] -= amount;
        totalStaked -= amount;
        _transfer(address(this), msg.sender, amount);
        
        emit Unstake(msg.sender, amount);
    }
    
    /**
     * @dev 分发挖矿奖励（仅合约所有者）
     */
    function distributeReward(address to, uint256 amount) external onlyOwner {
        require(balanceOf(address(this)) >= amount, "Insufficient reward pool");
        _transfer(address(this), to, amount);
        emit RewardDistributed(to, amount);
    }
    
    /**
     * @dev 检查并执行减半
     */
    function checkHalving() external {
        if (block.number >= lastHalvingBlock + HALVING_PERIOD) {
            miningRewardPerBlock = miningRewardPerBlock / 2;
            lastHalvingBlock = block.number;
        }
    }
    
    /**
     * @dev 获取当前挖矿奖励
     */
    function getCurrentMiningReward() external view returns (uint256) {
        return miningRewardPerBlock;
    }
    
    /**
     * @dev 转账时收取1%手续费，其中0.5%销毁
     */
    function _transfer(
        address sender,
        address recipient,
        uint256 amount
    ) internal virtual override {
        uint256 fee = amount / 100; // 1% 手续费
        uint256 burnAmount = fee / 2; // 0.5% 销毁
        uint256 transferAmount = amount - fee;
        
        super._transfer(sender, recipient, transferAmount);
        super._transfer(sender, address(this), fee - burnAmount);
        _burn(sender, burnAmount);
    }
}
