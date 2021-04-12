// SPDX-License-Identifier: MIT
pragma solidity >=0.7.0;

struct Logistics{
    string packageId;
    string vehicleType;
    string vehicleNo;
    string driverName;
    uint driverContact;
    uint dateDispatched;
}

contract LogisticsDetails{
    event LogDataAdded(string packageId);

    mapping (string => Logistics) logs;

    function addLogistic(string memory _packageId, string memory _vehicleType, string memory _vehicleNo, string memory _driverName, uint _driverContact, uint _dateDispatched)
    public {
        
        logs[_packageId].packageId = _packageId;
        logs[_packageId].vehicleType = _vehicleType;
        logs[_packageId].vehicleNo = _vehicleNo;
        logs[_packageId].driverName = _driverName;
        logs[_packageId].driverContact = _driverContact;
        logs[_packageId].dateDispatched = _dateDispatched;

        emit LogDataAdded(_packageId);
    }

    function getLog(string memory _packageId) view public
        returns(string memory, string memory, string memory, string memory, uint, uint, string memory) {
            return (logs[_packageId].packageId, logs[_packageId].vehicleType, logs[_packageId].vehicleNo, logs[_packageId].driverName, logs[_packageId].driverContact, logs[_packageId].dateDispatched, logs[_packageId].packageId);
        }
}