pragma solidity >=0.7.0;

struct Fpc{
    string name;
    string director;
    string phyAddr;
    string regNo;
    uint capacity;
}

contract FpcDetails{

    event FpcAdded(address indexed account);
    event UpdatedFpcDetails(address indexed account);

    mapping(address => Fpc) fpcs;
    address[] public fpcAccts;

    function addFpc(address _address, string memory _name, string memory _director, string memory _phyAddr, string memory _regNo, uint _capacity)
    public {
        fpcs[_address].name = _name;
        fpcs[_address].director = _director;
        fpcs[_address].phyAddr = _phyAddr;
        fpcs[_address].regNo = _regNo;
        fpcs[_address].capacity = _capacity;
        fpcAccts.push(_address);

        emit FpcAdded(_address);
    }

    function updateFpc(address _address, string memory _name, string memory _director, string memory _phyAddr, string memory _regNo, uint _capacity)
    public {
        
        fpcs[_address].name = _name;
        fpcs[_address].director = _director;
        fpcs[_address].phyAddr = _phyAddr;
        fpcs[_address].regNo = _regNo;
        fpcs[_address].capacity = _capacity;

        emit UpdatedFpcDetails(_address);
    }

    function getFpcs() view public returns(address[] memory){
        return fpcAccts;
    }
    
    function getFpc(address _address) view public 
        returns(string memory , string memory , string memory , string memory , uint){
            return (fpcs[_address].name, fpcs[_address].director, fpcs[_address].phyAddr, fpcs[_address].regNo, fpcs[_address].capacity);
    }
}