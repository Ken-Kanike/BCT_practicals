// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

contract CoursePayment {
    address public owner;
    uint256 public courseCount;
    uint256 public paymentCount;

    struct Course {
        string name;
        uint256 price;
        bool active;
    }

    struct Payment {
        address student;
        uint256 courseId;
        uint256 amount;
        uint256 timestamp;
    }

    mapping(uint256 => Course) public courses;
    mapping(address => mapping(uint256 => bool)) public hasPurchased;
    mapping(address => Payment[]) private studentPayments;
    Payment[] private allPayments;

    event CourseAdded(uint256 indexed courseId, string name, uint256 price);
    event CourseStatusChanged(uint256 indexed courseId, bool active);
    event CoursePurchased(
        address indexed student,
        uint256 indexed courseId,
        uint256 amount,
        uint256 timestamp
    );
    event Withdrawn(address indexed owner, uint256 amount);

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    function addCourse(string calldata name, uint256 price) external onlyOwner returns (uint256) {
        require(bytes(name).length > 0, "Course name required");
        require(price > 0, "Price must be positive");

        courseCount += 1;
        courses[courseCount] = Course(name, price, true);
        emit CourseAdded(courseCount, name, price);
        return courseCount;
    }

    function setCourseActive(uint256 courseId, bool active) external onlyOwner {
        require(courseId > 0 && courseId <= courseCount, "Unknown course");
        courses[courseId].active = active;
        emit CourseStatusChanged(courseId, active);
    }

    function purchaseCourse(uint256 courseId) external payable {
        require(courseId > 0 && courseId <= courseCount, "Unknown course");
        Course storage course = courses[courseId];
        require(course.active, "Course is not active");
        require(msg.value == course.price, "Incorrect payment amount");
        require(!hasPurchased[msg.sender][courseId], "Course already purchased");

        hasPurchased[msg.sender][courseId] = true;
        Payment memory payment = Payment(msg.sender, courseId, msg.value, block.timestamp);
        studentPayments[msg.sender].push(payment);
        allPayments.push(payment);
        paymentCount += 1;

        emit CoursePurchased(msg.sender, courseId, msg.value, block.timestamp);
    }

    function withdraw() external onlyOwner {
        uint256 balance = address(this).balance;
        require(balance > 0, "No funds to withdraw");

        (bool success, ) = payable(owner).call{value: balance}("");
        require(success, "Withdrawal failed");
        emit Withdrawn(owner, balance);
    }

    function getCourse(uint256 courseId)
        external
        view
        returns (string memory name, uint256 price, bool active)
    {
        require(courseId > 0 && courseId <= courseCount, "Unknown course");
        Course storage course = courses[courseId];
        return (course.name, course.price, course.active);
    }

    function getMyPayments() external view returns (Payment[] memory) {
        return studentPayments[msg.sender];
    }

    function getPayment(uint256 index) external view returns (Payment memory) {
        require(index < allPayments.length, "Invalid payment index");
        return allPayments[index];
    }

    function getContractBalance() external view returns (uint256) {
        return address(this).balance;
    }
}
