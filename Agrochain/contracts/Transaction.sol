// SPDX-License-Identifier: MIT
pragma solidity >=0.7.0;
pragma experimental ABIEncoderV2;

struct Transaction{

    string packageId;
    uint sellerType;
    string sellerName;
    uint buyerType;
    string buyerName;
    uint cropId;
    string cropName;
    string grade;
    uint price;
    uint quantity;
    uint remainingQuantity;
    string prevId;
    string nextId;
    bool active;
    address sellerAddress;
}

contract TransactionDetails{
    event FarmerToHubTransactionAdded(string sellerName, string buyerName);
    event HubToRetailerTransactionAdded(string sellerName, string buyerName);
    event RetailerToCustomerTransactionAdded(string sellerName);

    mapping (string => Transaction) txns;
    mapping (address => string[]) entityTxns;

    function f2hTransaction(address seller, address buyer, string memory _packageId, string memory _sellerName, string memory _buyerName, uint _cropId, string memory _cropName, uint _price, uint _quantity)
    public {
        Transaction memory new_txn = Transaction(_packageId, 0, _sellerName, 1, _buyerName, _cropId, _cropName,"", _price, _quantity, _quantity, "", "", true, seller);

        // new_txn.packageId = _packageId;
        // new_txn.sellerType = 0;
        // new_txn.sellerName = _sellerName;
        // new_txn.buyerType = 1;
        // new_txn.buyerName = _buyerName;
        // new_txn.crop = _crop;
        // new_txn.price = _price;
        // new_txn.quantity = _quantity;
        // new_txn.prevId = "";

        txns[_packageId] = new_txn;
        entityTxns[seller].push(_packageId);
        entityTxns[buyer].push(_packageId);

        emit FarmerToHubTransactionAdded(_sellerName, _buyerName);
    }

    function h2rTransaction(address seller, address buyer, string memory _packageId, string memory _sellerName, string memory _buyerName, uint _cropId, string memory _cropName,string memory _grade, uint _price, uint _quantity, string memory _prevId)
    public {
        Transaction memory new_txn = Transaction(_packageId, 1, _sellerName, 2, _buyerName, _cropId, _cropName,_grade, _price, _quantity, _quantity, _prevId, "", true, seller);
        txns[_prevId].remainingQuantity = txns[_prevId].remainingQuantity - _quantity;

        if(txns[_prevId].remainingQuantity == 0){
            txns[_prevId].active = false;
        }
        

        // new_txn.packageId = _packageId;
        // new_txn.sellerType = 1;
        // new_txn.sellerName = _sellerName;
        // new_txn.buyerType = 2;
        // new_txn.buyerName = _buyerName;
        // new_txn.crop = _crop;
        // new_txn.grade = _grade;
        // new_txn.price = _price;
        // new_txn.quantity = _quantity;
        // new_txn.packageId = _packageId;
        // new_txn.prevId = _prevId;

        txns[_packageId] = new_txn;
        entityTxns[buyer].push(_packageId);
        entityTxns[seller].push(_packageId);
    }

    function r2cTransaction(address seller, string memory _packageId, string memory _sellerName, uint _cropId, string memory _cropName, uint _price, uint _quantity, string memory _prevId)
    public {
        Transaction memory new_txn = Transaction(_packageId, 2, _sellerName, 3, "", _cropId, _cropName , "",  _price, _quantity, 0, _prevId, "", false, seller);
        txns[_prevId].remainingQuantity = txns[_prevId].remainingQuantity - _quantity;
        //if all crop quantity is exhausted, make prev h2r txn inactive
        if(txns[_prevId].remainingQuantity == 0){
            txns[_prevId].active = false;
        }

        txns[_packageId] = new_txn;
        entityTxns[seller].push(_packageId);

        emit RetailerToCustomerTransactionAdded(_sellerName);
    }
    
    function getTransactions(address _address) view public
        returns(string[] memory){
            return entityTxns[_address];
        }

    function getTxnCropDetails(string memory tid) view public
    returns(uint, string memory,string memory, uint, uint, uint) {
        return(txns[tid].cropId, txns[tid].cropName, txns[tid].grade, txns[tid].price, txns[tid].quantity, txns[tid].remainingQuantity);
    }

    function getTxnEntityDetails(string memory tid) view public
    returns(uint, string memory, uint, string memory, address _address){
        return(txns[tid].sellerType, txns[tid].sellerName, txns[tid].buyerType, txns[tid].buyerName, txns[tid].sellerAddress);
    }

    function getPrevId(string memory tid) view public
    returns(string memory) {
        return(txns[tid].prevId);
    }

    function getNextId(string memory tid) view public
    returns(string memory) {
        return(txns[tid].nextId);
    }

    function getActiveStatus(string memory tid) view public 
    returns(bool) {
        return(txns[tid].active);
    }

    function setNextHash(string memory tid, string memory _nextHash)
    public {
        txns[tid].nextId = _nextHash;
    }
}