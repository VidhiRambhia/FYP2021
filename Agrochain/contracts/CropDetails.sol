// SPDX-License-Identifier: MIT
pragma solidity >=0.7.0;

struct Crop{
    uint cropID;
    string cropType;
    string cropName; 
    string fertiliser;
    string sourceTagNo;
    uint quantity;
    //uint256 DateSowed;
    uint256 DateHarvested;
    bool sold;
}

contract CropDetails{
    
    //event when farmer is added
    event CropAdded(address indexed account);
    event CropUpdated(address indexed account);
    
    mapping(address=>Crop[]) public crops;
    
    function addCrop1(string calldata cropType, string calldata cropName, string calldata sourceTagNo,
         address farmerAddr) public returns (uint cropID){
            Crop memory crop;
            crop.cropID = crops[farmerAddr].length;
            crop.cropType = cropType;
            crop.cropName = cropName;
            crop.sourceTagNo = sourceTagNo;
            crops[farmerAddr].push(crop);
            return crop.cropID;
        }
        
    function addCrop2(uint cropID, string memory fertiliser, uint quantity,
        uint256 DateHarvested, address farmerAddr) public{
            Crop storage crop = crops[farmerAddr][cropID];
            crop.fertiliser = fertiliser;
            crop.quantity = quantity;
            //crop.DateSowed = DateSowed;
            crop.DateHarvested = DateHarvested;
            crop.sold = false;
            emit CropAdded(farmerAddr);
        }
        
    function updateCrop(uint cropID, address farmerAddr, uint256 DateHarvested, uint quantity, bool sold) public{
        Crop storage crop = crops[farmerAddr][cropID];
        crop.DateHarvested = DateHarvested;
        crop.quantity = quantity;
        crop.sold = sold;
        emit CropUpdated(farmerAddr);
    }
    
    function getCrop1(address farmerAddr, uint cropID) view public returns (string memory cropType, string memory cropName,
    string memory sourceTagNo, bool sold){
        return (crops[farmerAddr][cropID].cropType, crops[farmerAddr][cropID].cropName,
            crops[farmerAddr][cropID].sourceTagNo, crops[farmerAddr][cropID].sold);
    }
        
    function getCrop2(address farmerAddr, uint cropID) view public returns (string memory fertiliser,uint quantity,
         uint256 DateHarvested){
            return (crops[farmerAddr][cropID].fertiliser, crops[farmerAddr][cropID].quantity,
                crops[farmerAddr][cropID].DateHarvested);
    }

    function setSold(uint cropID, address farmerAddr) public{
        Crop storage crop = crops[farmerAddr][cropID];
        crop.sold = true;
        emit CropUpdated(farmerAddr);
    }
}