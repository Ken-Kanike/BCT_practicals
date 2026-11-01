// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title Wallet
/// @notice A simple custodial wallet contract that demonstrates Solidity
///         state, events, modifiers, payable functions and access control.
contract Wallet {
    address public owner;

    event Deposit(address indexed sender, uint256 amount);
    event Withdraw(address indexed recipient, uint256 amount);

    modifier onlyOwner() {
        require(msg.sender == owner, "Wallet: caller is not the owner");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    /// @notice Deposit ETH into the contract.
    function deposit() external payable {
        require(msg.value > 0, "Wallet: deposit must be greater than zero");
        emit Deposit(msg.sender, msg.value);
    }

    /// @notice Withdraw ETH from the contract. Only the owner may withdraw.
    function withdraw(uint256 amount) external onlyOwner {
        require(address(this).balance >= amount, "Wallet: insufficient balance");
        (bool success, ) = payable(msg.sender).call{value: amount}("");
        require(success, "Wallet: transfer failed");
        emit Withdraw(msg.sender, amount);
    }

    /// @notice Current contract balance in wei.
    function getBalance() external view returns (uint256) {
        return address(this).balance;
    }

    /// @notice Plain ETH transfers are treated as deposits.
    receive() external payable {
        emit Deposit(msg.sender, msg.value);
    }
}
