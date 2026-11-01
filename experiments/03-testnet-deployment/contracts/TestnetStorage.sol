// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title TestnetStorage
/// @notice Small contract used to demonstrate the full deployment and
///         publishing workflow on an Ethereum test network.
contract TestnetStorage {
    uint256 private value;
    address public immutable deployer;

    event ValueChanged(address indexed by, uint256 oldValue, uint256 newValue);

    constructor(uint256 initialValue) {
        deployer = msg.sender;
        value = initialValue;
        emit ValueChanged(msg.sender, 0, initialValue);
    }

    function setValue(uint256 newValue) external {
        uint256 oldValue = value;
        value = newValue;
        emit ValueChanged(msg.sender, oldValue, newValue);
    }

    function getValue() external view returns (uint256) {
        return value;
    }
}
