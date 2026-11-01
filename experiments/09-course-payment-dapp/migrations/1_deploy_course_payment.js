const CoursePayment = artifacts.require("CoursePayment");

module.exports = async function (deployer) {
  await deployer.deploy(CoursePayment);
  const app = await CoursePayment.deployed();

  await app.addCourse("Blockchain Fundamentals", web3.utils.toWei("0.5", "ether"));
  await app.addCourse("Smart Contract Security", web3.utils.toWei("0.75", "ether"));
  await app.addCourse("DeFi Essentials", web3.utils.toWei("1", "ether"));
};
