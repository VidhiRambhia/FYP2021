import json
import sys
import datetime
import hashlib
from web3 import Web3, HTTPProvider,IPCProvider
from flask import Flask, render_template, request, redirect, url_for
from config import config

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



cropDetails_contract_address = config.cropDetails_contract_address
farmerDetails_contract_address = config.farmerDetails_contract_address
login_contract_address = config.login_contract_address 

w3 = Web3(HTTPProvider("http://localhost:7545"))
# IPC Provider error here
eth = Web3(IPCProvider()).eth

print(w3.isConnected())

# # Initialize a local account object from the private key of a valid Ethereum node address
# # Add your own private key here
local_acct = w3.eth.account.from_key(config.local_acct_key)

# # compile your smart contract with truffle first
cropDetails_truffleFile = json.load(open('./build/contracts/CropDetails.json'))
cropDetails_abi = cropDetails_truffleFile['abi']

farmerDetails_truffleFile = json.load(open('./build/contracts/FarmerDetails.json'))
farmerDetails_abi = farmerDetails_truffleFile['abi']

login_truffleFile = json.load(open('./build/contracts/Login.json'))
login_abi = login_truffleFile['abi']


# # Initialize a contract object with the smart contract compiled artifacts
cropDetails_contract_instance = w3.eth.contract(abi=cropDetails_abi, address=cropDetails_contract_address)
farmerDetails_contract_instance = w3.eth.contract(abi=farmerDetails_abi, address=farmerDetails_contract_address)
login_contract_instance = w3.eth.contract(abi=login_abi, address=login_contract_address)

app = Flask(__name__)

def addNewUser(email, pwd_hash, role):
    user_dict = {
            'from': local_acct.address,
            'to': login_contract_address,
            'value': 0,
            'gas':2000000,
            'gasPrice': w3.toWei('40', 'gwei')
        }
    txn_hash = login_contract_instance.functions.addUser(local_acct.address, email, pwd_hash, role).transact(user_dict)
    print('new user added', txn_hash)

def verifyUser(address):
    user_dict = {
            'from': local_acct.address,
            'to': login_contract_address,
            'value': 0,
            'gas':2000000,
            'gasPrice': w3.toWei('40', 'gwei')
        }
    print('creating transaction')
    txn_hash = login_contract_instance.functions.getUser(address).transact(user_dict)
    print(eth.getTransactionReceipt(txn_hash))


@app.route("/home")
@app.route("/", methods=["GET","POST"])
def index():
    #print(cropDetails_contract_instance.functions.getCrop2(local_acct.address,11).call())
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
    if request.method == "POST":
        email = request.form.get('email') 
        password = request.form.get('password')
        pwd_hash = hashlib.sha256(password.encode()).hexdigest()
        addNewUser(email, pwd_hash, 'farmer')

        plot_number = request.form.get('plot_number')
        plot_owner = request.form.get('plot_owner')
        plot_address = request.form.get('plot_address')
        txn_dict = {
                'from': local_acct.address,
                'to': farmerDetails_contract_address,
                'value': '0',
                'gas': 2000000,
                'gasPrice': w3.toWei('40', 'gwei')
                }
        farmer_address = "0x0" #get address
        txn_hash = farmerDetails_contract_instance.functions.addFarmer(local_acct.address,email,plot_owner,plot_number,plot_address,True).transact(txn_dict)
        print(txn_hash)

        if request.form.get('plot_number_1'):
            plot_number_1 = request.form.get('plot_number_1')
            plot_owner_1 = request.form.get('plot_owner_1')
            plot_address_1 = request.form.get('plot_address_1')
            txn_hash = farmerDetails_contract_instance.functions.addPlot(farmer_address,plot_owner,plot_number,plot_address).transact(txn_dict)
            print(txn_hash)
        if request.form.get('plot_number_2'):
            plot_number_2 = request.form.get('plot_number_2')
            plot_owner_2 = request.form.get('plot_owner_2')
            plot_address_2 = request.form.get('plot_address_2')
            txn_hash = farmerDetails_contract_instance.functions.addPlot(farmer_address,plot_owner,plot_number,plot_address).transact(txn_dict)
            print(txn_hash)
    return render_template('registerFarmer.html')


@app.route("/chooseRole", methods=["GET","POST"])
def chooseRole():
    if(request.method=="POST"):
        selectedRole = request.form.get('role')
        print('selected role: ', selectedRole)
        if (selectedRole == 'farmer'):
            return redirect(url_for('registerFarmer'))
        else:
            return redirect(url_for('chooseRole'))
    return render_template('ChooseRole.html')

@app.route("/addCropDetails",methods=["GET","POST"])
def addcropDetails():
    if request.method=="POST":
        crop_name = request.form.get('crop_name')
        crop_type = request.form.get('crop_type')
        fertilizer = request.form.get('fertilizer')
        quantity = int(request.form.get('quantity'))
        source_tag_number = request.form.get('source_tag_number')
        sowing_date = request.form.get('sowing_date')
        harvesting_date = request.form.get('harvesting_date')
        txn_dict = {
                'from': local_acct.address,
                'to': cropDetails_contract_address,
                'value': '0',
                'gas': 3000000,
                'gasPrice': w3.toWei('40', 'gwei')
                }
        farmer_address = "0x0" #get address
        sowing_date = datetime.datetime(*[int(item) for item in sowing_date.split('-')])
        sowing_date_int = int(sowing_date.strftime('%Y%m%d'))
        #harvesting_date_int= 1
        crop_id = cropDetails_contract_instance.functions.addCrop1(crop_type,crop_name,source_tag_number,local_acct.address).call()
        txn_hash = cropDetails_contract_instance.functions.addCrop1(crop_type,crop_name,source_tag_number,local_acct.address).transact(txn_dict)
        txn_hash = cropDetails_contract_instance.functions.addCrop2(int(crop_id),fertilizer,quantity,sowing_date_int, local_acct.address).transact(txn_dict)
        #print(txn_hash)
        print(crop_id)
    return render_template('addCropDetails.html')

@app.route("/farmerPage", methods=["GET","POST"])
def farmerPage():
    if request.method=="POST":
        if 'profile' in request.form:
            return redirect(url_for('registerFarmer'))
        elif 'addCrop' in request.form:
            return redirect(url_for('cropDetails'))
        elif 'updateCrop' in request.form:
            return redirect(url_for('cropDetails'))

    return render_template('FarmerFunctions.html')

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        print(email)
        password = request.form.get('password')
        pwd_hash = hashlib.sha256(password.encode()).hexdigest()

        verifyUser(email)
        redirect(url_for('farmerPage'))
    return render_template("Login.html")


@app.route("/error")
def error():
    return render_template('error.html')


if __name__ == '__main__':
    app.run(debug=True)

