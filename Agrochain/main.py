import json
import sys
from web3 import Web3, HTTPProvider
from flask import Flask, render_template, request

# create a web3.py instance w3 by connecting to the local Ethereum node
w3 = Web3(HTTPProvider("http://localhost:7545"))

print(w3.isConnected())

# Initialize a local account object from the private key of a valid Ethereum node address
# local_acct = w3.eth.account.from_key("5a6176b5656256b81c08e0fdccb80b797da80292f37c4e06e2a089a93d68ecb4")
local_acct = w3.eth.account.from_key("d369e8188b5900d928bdd2965f39adc6c7cec1c5b510cd5d6f50ffbd8ef3ca5f")
# compile your smart contract with truffle first
truffleFile = json.load(open('./build/contracts/Migrations.json'))
abi = truffleFile['abi']
bytecode = truffleFile['bytecode']

# Initialize a contract object with the smart contract compiled artifacts
contract = w3.eth.contract(bytecode=bytecode, abi=abi)

# build a transaction by invoking the buildTransaction() method from the smart contract constructor function
construct_txn = contract.constructor(60, '0xA72c3f7E17568BBc5B3D0E4466176fad85180681').buildTransaction({
    'from': local_acct.address,
    'nonce': w3.eth.getTransactionCount(local_acct.address),
    'gas': 1728712,
    'gasPrice': w3.toWei('21', 'gwei')})

# sign the deployment transaction with the private key
signed = w3.eth.account.sign_transaction(construct_txn, local_acct.key)

# broadcast the signed transaction to your local network using sendRawTransaction() method and get the transaction hash
tx_hash = w3.eth.sendRawTransaction(signed.rawTransaction)
print(tx_hash.hex())

# collect the Transaction Receipt with contract address when the transaction is mined on the network
tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
print("Contract Deployed At:", tx_receipt['contractAddress'])
contract_address = tx_receipt['contractAddress']

# Initialize a contract instance object using the contract address which can be used to invoke contract functions
contract_instance = w3.eth.contract(abi=abi, address=contract_address)

#event_filter = contract_instance.events.AuctionEnded.createFilter(fromBlock='latest')


app = Flask(__name__)


@app.route("/")
def index():
    print(contract_address)
    print(w3.isConnected())
    return render_template('index.html')


@app.route("/error")
def error():
    return render_template('error.html')


if __name__ == '__main__':
    app.run(debug=True)

