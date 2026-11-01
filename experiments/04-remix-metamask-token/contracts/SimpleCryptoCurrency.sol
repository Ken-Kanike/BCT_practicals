// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title SimpleCryptoCurrency
/// @notice A minimal ERC-20-style cryptocurrency. It can be pasted directly
///         into Remix IDE and deployed through MetaMask (Injected Web3).
///         The contract keeps the `balances` mapping used in the lab manual
///         and also exposes the standard `balanceOf` / `allowance` interface.
contract SimpleCryptoCurrency {
    string public name;
    string public symbol;
    uint8 public decimals;
    uint256 public totalSupply;
    address public owner;

    mapping(address => uint256) public balances;
    mapping(address => mapping(address => uint256)) public allowance;

    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);

    constructor(
        string memory _name,
        string memory _symbol,
        uint8 _decimals,
        uint256 _initialSupply
    ) {
        owner = msg.sender;
        name = _name;
        symbol = _symbol;
        decimals = _decimals;
        totalSupply = _initialSupply * 10 ** uint256(_decimals);
        balances[msg.sender] = totalSupply;
        emit Transfer(address(0), msg.sender, totalSupply);
    }

    function balanceOf(address account) external view returns (uint256) {
        return balances[account];
    }

    function transfer(address to, uint256 value) public returns (bool) {
        require(to != address(0), "Token: transfer to zero address");
        require(balances[msg.sender] >= value, "Token: insufficient balance");

        balances[msg.sender] -= value;
        balances[to] += value;
        emit Transfer(msg.sender, to, value);
        return true;
    }

    function approve(address spender, uint256 value) external returns (bool) {
        allowance[msg.sender][spender] = value;
        emit Approval(msg.sender, spender, value);
        return true;
    }

    function transferFrom(address from, address to, uint256 value) external returns (bool) {
        require(to != address(0), "Token: transfer to zero address");
        require(balances[from] >= value, "Token: insufficient balance");
        require(allowance[from][msg.sender] >= value, "Token: insufficient allowance");

        allowance[from][msg.sender] -= value;
        balances[from] -= value;
        balances[to] += value;
        emit Transfer(from, to, value);
        return true;
    }
}
