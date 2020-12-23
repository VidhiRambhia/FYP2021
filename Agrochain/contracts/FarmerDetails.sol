pragma solidity ^0.7.0;

struct Plot{
    string owner;
    string plotNumber;
    string plotAddress;
}

struct Farmer{
   string name;
   Plot[] plots;
   bool approved;
}

contract FarmerDetails{
    
    //event when farmer is added
    event FarmerAdded(address indexed account);
    event PlotAdded(address indexed account);
    
    mapping(address =>Farmer) farmers;
    address[] public farmerAccts;
    
    function addFarmer(address _address, string memory _farmerName, string memory _plotOwner, string memory _plotNumber, string memory _plotAddress, bool _approved) 
        public{
        
        farmers[_address].plots.push(Plot(_plotOwner,_plotNumber,_plotAddress));
        farmers[_address].name = _farmerName;
        farmers[_address].approved = _approved;
        farmerAccts.push(_address);
        emit FarmerAdded(_address);
        
    }
    
    function addPlot(address _address, string memory _plotOwner, string memory _plotNumber, string memory _plotAddress)
        public{
        farmers[_address].plots.push(Plot(_plotOwner,_plotNumber,_plotAddress));
        emit PlotAdded(_address);
    }
    
    function getFarmers() view public returns(address[] memory){
        return farmerAccts;
    }
    
    function getFarmer(address _address, uint index) view public 
        returns(string memory , string memory , string memory , string memory , bool){
            return (farmers[_address].name, farmers[_address].plots[index].owner, farmers[_address].plots[index].plotNumber, farmers[_address].plots[index].plotAddress, farmers[_address].approved);
    }
    
}