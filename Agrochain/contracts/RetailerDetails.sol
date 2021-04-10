// SPDX-License-Identifier: MIT
pragma solidity >=0.7.0;

struct Retailer{
    string name;
    string addr;
    string city;
    string regNo;
}

contract RetailerDetails{

    event RetailerAdded(address indexed account);
    event RetailerUpdated(address indexed account);

    mapping (address => Retailer) retailers;
    address[] public retailerAccts;

    function addRetailer(address _address, string memory _name, string memory _addr, string memory _city, string memory _regNo) 
    public {
        retailerAccts.push(_address);

        retailers[_address].name = _name;
        retailers[_address].addr = _addr;
        retailers[_address].city = _city;
        retailers[_address].regNo = _regNo;

        emit RetailerAdded(_address);
    }

    function updateRetailer(address _address, string memory _name, string memory _addr, string memory _city, string memory _regNo) 
    public {

        retailers[_address].name = _name;
        retailers[_address].addr = _addr;
        retailers[_address].city = _city;
        retailers[_address].regNo = _regNo;

        emit RetailerUpdated(_address);
    }

    function getRetailers() view public 
    returns(address[] memory){
        return retailerAccts;
    }

    function getRetailer(address _address) view public
    returns(string memory, string memory, string memory, string memory) {
        return(retailers[_address].name, retailers[_address].addr, retailers[_address].city, retailers[_address].regNo);
    }
}