pragma solidity ^0.7.0;

struct User{
    string pwdHash;
    string role;
    address addr;
}

contract Login{
    
    mapping(string=>User) users;
    
    function addUser(address addr, string memory email, string memory pwdHash, string memory role) public{
        users[email].pwdHash = pwdHash;
        users[email].role = role;
        users[email].addr = addr;
    }
    
    function getUser(string memory email) view public returns(string memory pwdHash, string memory role, address addr){
        return (users[email].pwdHash, users[email].role, users[email].addr);
    }
}