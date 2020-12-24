pragma solidity ^0.7.0;

struct User{
    string pwdHash;
    string role;
}

contract Login{
    
    mapping(address=>User) users;
    
    function addUser(address addr, string memory pwdHash, string memory role) public{
        users[addr].pwdHash = pwdHash;
        users[addr].role = role;
    }
    
    function getUser(address addr) view public returns(string memory pwdHash, string memory role){
        return (users[addr].pwdHash, users[addr].role);
    }
}