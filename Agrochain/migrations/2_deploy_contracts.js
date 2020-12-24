const Migrations = artifacts.require("Migrations");

module.exports = function (deployer) {
  biddingTime = 3000;
  beneficiary = '0x6Ef4724927cca14ac42Cb775fB55a6ab65451A8E';
  deployer.deploy(Migrations,biddingTime,beneficiary);
};

