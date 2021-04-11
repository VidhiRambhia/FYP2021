// SPDX-License-Identifier: MIT
pragma solidity >=0.7.0;

struct Logistics{
    uint id;
    string vehicleType;
    string vehicleNo;
    string driverName;
    uint driverContact;
    uint dateDispatched;
    string packageId;
}

contract LogisticsDetails{
    event LogDataAdded(uint LogId);

    mapping (uint => Logistics) logs;
    uint[] public LogIds;

    function addLogistic(uint _id, string memory _vehicleType, string memory _vehicleNo, string memory _driverName, uint _driverContact, uint _dateDispatched, string memory _packageId)
    public {
        LogIds.push(_id);
        logs[_id].id = _id;
        logs[_id].vehicleType = _vehicleType;
        logs[_id].vehicleNo = _vehicleNo;
        logs[_id].driverName = _driverName;
        logs[_id].driverContact = _driverContact;
        logs[_id].dateDispatched = _dateDispatched;
        logs[_id].packageId = _packageId;

        emit LogDataAdded(_id);
    }

    function getAllLogs() view public returns(uint[] memory){
        return LogIds;
    }

    function getLog(uint LID) view public
        returns(uint, string memory, string memory, string memory, uint, uint, string memory) {
            return (logs[LID].id, logs[LID].vehicleType, logs[LID].vehicleNo, logs[LID].driverName, logs[LID].driverContact, logs[LID].dateDispatched, logs[LID].packageId);
        }
}