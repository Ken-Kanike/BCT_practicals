const fs = require("fs");
const path = require("path");
const CoursePayment = artifacts.require("CoursePayment");

module.exports = async function () {
  const app = await CoursePayment.deployed();
  const networkId = await web3.eth.net.getId();

  const deployment = {
    address: app.address,
    networkId: networkId.toString(),
    abi: CoursePayment.abi,
  };

  const outPath = path.join(__dirname, "..", "ui", "deployment.json");
  fs.writeFileSync(outPath, JSON.stringify(deployment, null, 2));
  console.log(`Wrote deployment to ${outPath}`);
};
