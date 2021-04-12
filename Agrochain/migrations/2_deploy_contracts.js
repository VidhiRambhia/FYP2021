const CropDetails = artifacts.require("CropDetails");
const FarmerDetails = artifacts.require("FarmerDetails");
const FpcDetails = artifacts.require("FpcDetails");
const RetailerDetails = artifacts.require("RetailerDetails");
const LogisticsDetails = artifacts.require("LogisticsDetails");
const TransactionDetails = artifacts.require("TransactionDetails");

module.exports = function (deployer) {
  deployer.deploy(CropDetails);
  deployer.deploy(FarmerDetails); 
  deployer.deploy(FpcDetails);
  deployer.deploy(RetailerDetails);
  deployer.deploy(LogisticsDetails);
  deployer.deploy(TransactionDetails);
};

