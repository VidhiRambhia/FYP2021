import json
import sys
from web3 import Web3, HTTPProvider
from flask import Flask, render_template, request, redirect, url_for

# # create a web3.py instance w3 by connecting to the local Ethereum node
# w3 = Web3(HTTPProvider("http://localhost:7545"))

# print(w3.isConnected())

# # Initialize a local account object from the private key of a valid Ethereum node address
# # Add your own private key here
# local_acct = w3.eth.account.from_key("3b4a60ab47652548c19663d1ae02703da2eb2f92434f304d87f12abc5fad567b")

# # compile your smart contract with truffle first
# truffleFile = json.load(open('./build/contracts/Migrations.json'))
# abi = truffleFile['abi']
# bytecode = truffleFile['bytecode']

# # Initialize a contract object with the smart contract compiled artifacts
# contract = w3.eth.contract(bytecode=bytecode, abi=abi)

# # build a transaction by invoking the buildTransaction() method from the smart contract constructor function
# # Add your own account address here

# construct_txn = contract.constructor(60, '0x8E73855be1b32A8a3693eB2b15503EDd51939a3E').buildTransaction({

#     'from': local_acct.address,
#     'nonce': w3.eth.getTransactionCount(local_acct.address),
#     'gas': 1728712,
#     'gasPrice': w3.toWei('21', 'gwei')})

# # sign the deployment transaction with the private key
# signed = w3.eth.account.sign_transaction(construct_txn, local_acct.key)

# # broadcast the signed transaction to your local network using sendRawTransaction() method and get the transaction hash
# tx_hash = w3.eth.sendRawTransaction(signed.rawTransaction)
# print(tx_hash.hex())

# # collect the Transaction Receipt with contract address when the transaction is mined on the network
# tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
# print("Contract Deployed At:", tx_receipt['contractAddress'])
# contract_address = tx_receipt['contractAddress']

# # Initialize a contract instance object using the contract address which can be used to invoke contract functions
# contract_instance = w3.eth.contract(abi=abi, address=contract_address)

# #event_filter = contract_instance.events.AuctionEnded.createFilter(fromBlock='latest')


app = Flask(__name__)

@app.route("/", methods=["GET","POST"])
def index():
    #print(contract_address)
    #print(w3.isConnected())
    if(request.method == "POST"):
        return redirect(url_for('login'))
    email = request.form.get('email') #Todo: Add other fields
    return render_template('home.html')


@app.route("/registerFarmer",methods=["GET","POST"])
def registerFarmer():
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


@app.route("/chooseRole", methods=["GET","POST"])
def chooseRole():
    if(request.method=="POST"):
        selectedRole = request.form.get('role')
        print('selected role: ', selectedRole)
        if (selectedRole == 'farmer'):
            return redirect(url_for('index'))
        else:
            return redirect(url_for('chooseRole'))
    return render_template('ChooseRole.html')

@app.route("/cropDetails")
def cropDetails():
    return render_template('CropDetails.html')

@app.route("/farmerPage", methods=["GET","POST"])
def farmerPage():
    if request.method=="POST":
        if 'profile' in request.form:
            return redirect(url_for('index'))
        elif 'addCrop' in request.form:
            return redirect(url_for('cropDetails'))
        elif 'updateCrop' in request.form:
            return redirect(url_for('cropDetails'))

    return render_template('FarmerFunctions.html')

@app.route("/login")
def login():
    return render_template("Login.html")


# @app.route("/registerFarmer")
# def registerFarmer():
#     return render_template('FarmerFunctions.html')

@app.route("/addCrop")
def addCrop():
    return render_template('addCropDetails.html')

@app.route("/error")
def error():
    return render_template('error.html')


if __name__ == '__main__':
    app.run(debug=True)

