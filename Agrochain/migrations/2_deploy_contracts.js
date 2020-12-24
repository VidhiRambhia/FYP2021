const CropDetails = artifacts.require("CropDetails");
const FarmerDetails = artifacts.require("FarmerDetails");
const User = artifacts.require("Login");

module.exports = function (deployer) {
  deployer.deploy(CropDetails);
  deployer.deploy(FarmerDetails);
  deployer.deploy(User);  
};

