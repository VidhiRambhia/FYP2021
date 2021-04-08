pragma solidity >=0.7.0;

struct Transaction{
    uint tid;
    uint sellerType;
    string sellerName;
    uint buyerType;
    string buyerName;
    string crop;
    string grade;
    uint price;
    uint quantity;
    string packageId;
    uint logisticId;
    bytes prevHash;
    bytes nextHash;
}

contract TransactionDetails{
    event FarmerToHubTransactionAdded(string sellerName, string buyerName);
    event HubToRetailerTransactionAdded(string sellerName, string buyerName);

    mapping (uint => Transaction) txns;
    uint[] tids;

    function f2hTransaction(uint _tid, string memory _sellerName, string memory _buyerName, string memory _crop, uint _price, uint _quantity, uint _logisticId)
    public {
        tids.push(_tid);

        txns[_tid].tid = _tid;
        txns[_tid].sellerType = 0;
        txns[_tid].sellerName = _sellerName;
        txns[_tid].buyerType = 1;
        txns[_tid].buyerName = _buyerName;
        txns[_tid].crop = _crop;
        txns[_tid].price = _price;
        txns[_tid].quantity = _quantity;
        txns[_tid].logisticId = _logisticId;
        txns[_tid].prevHash = "";

        emit FarmerToHubTransactionAdded(_sellerName, _buyerName);
    }

    function h2rTransaction(uint _tid, string memory _sellerName, string memory _buyerName, string memory _crop, string memory _grade, uint _price, uint _quantity, string memory _packageId, uint _logisticId, bytes memory _prevHash)
    public {
        tids.push(_tid);

        txns[_tid].tid = _tid;
        txns[_tid].sellerType = 1;
        txns[_tid].sellerName = _sellerName;
        txns[_tid].buyerType = 2;
        txns[_tid].buyerName = _buyerName;
        txns[_tid].crop = _crop;
        txns[_tid].grade = _grade;
        txns[_tid].price = _price;
        txns[_tid].quantity = _quantity;
        txns[_tid].packageId = _packageId;
        txns[_tid].logisticId = _logisticId;
        txns[_tid].prevHash = _prevHash;
    }
    
    function getTransactions() view public
        returns(uint[] memory){
            return tids;
        }

    function getTxn(uint tid) view public
    returns(uint, string memory, uint, string memory, string memory, string memory, uint, uint, string memory, uint, bytes memory, bytes memory) {
        return(txns[tid].sellerType, txns[tid].sellerName, txns[tid].buyerType, txns[tid].buyerName, txns[tid].crop, txns[tid].grade,
                txns[tid].price, txns[tid].quantity, txns[tid].packageId, txns[tid].logisticId, txns[tid].prevHash, txns[tid].nextHash);
    }

    function setNextHash(uint tid, bytes memory _nextHash)
    public {
        txns[tid].nextHash = _nextHash;
    }
}