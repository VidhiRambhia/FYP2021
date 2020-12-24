import json
import sys
from web3 import Web3, HTTPProvider
from flask import Flask, render_template, request

# create a web3.py instance w3 by connecting to the local Ethereum node
w3 = Web3(HTTPProvider("http://localhost:7545"))

print(w3.isConnected())

# Initialize a local account object from the private key of a valid Ethereum node address
# Add your own private key here
local_acct = w3.eth.account.from_key("f6f9d4c2d90707ca947c5dba2eb531659883ec24f69aa5b0ea65c251b99b5e01")

# compile your smart contract with truffle first
truffleFile = json.load(open('./build/contracts/Migrations.json'))
abi = truffleFile['abi']
bytecode = truffleFile['bytecode']

# Initialize a contract object with the smart contract compiled artifacts
contract = w3.eth.contract(bytecode=bytecode, abi=abi)

# build a transaction by invoking the buildTransaction() method from the smart contract constructor function
# Add your own account address here
construct_txn = contract.constructor(60, '0x25968ea7d119fea4bb20CFd9e06E737a25e13bE3').buildTransaction({
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


@app.route("/registerFarmer",methods=["GET","POST"])
def index():
    #print(contract_address)
    #print(w3.isConnected())
    #print(request.form)
    email = request.form.get('email') 
    password = request.form.get('password')
    plot_number = request.form.get('plot_number')
    plot_owner = request.form.get('plot_owner')
    plot_address = request.form.get('plot_address')
    # Call add plot here
    if request.form.get('plot_number_1'):
        plot_number_1 = request.form.get('plot_number_1')
        plot_owner_1 = request.form.get('plot_owner_1')
        plot_address_1 = request.form.get('plot_address_1')
        # Call add plot again 
    if request.form.get('plot_number_2'):
        plot_number_2 = request.form.get('plot_number_2')
        plot_owner_2 = request.form.get('plot_owner_2')
        plot_address_2 = request.form.get('plot_address_2')
        # Call add plot again 
    return render_template('registerFarmer.html')


@app.route("/registerFarmer")
def registerFarmer():
    return render_template('FarmerFunctions.html')

@app.route("/addCrop")
def addCrop():
    return render_template('addCropDetails.html')

@app.route("/chooseRole")
def chooseRole():
    return render_template('ChooseRole.html')

@app.route("/error")
def error():
    return render_template('error.html')


if __name__ == '__main__':
    app.run(debug=True)

