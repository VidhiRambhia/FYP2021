import json
import sys
import datetime
import hashlib
import os
import time
from web3 import Web3, HTTPProvider,IPCProvider
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask,Blueprint, render_template, request, redirect, url_for,flash
from flask_login import UserMixin, LoginManager, login_user, login_required, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from flaskapp.config import config
from flaskapp.models import User
from flaskapp import db,w3,eth,app
from flaskapp.Role import ROLE
from eth_account import Account

mod_fpc = Blueprint('fpc', __name__, url_prefix='')

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#db.create_all()

# @Vidhi modify
# cropDetails_contract_address = config.cropDetails_contract_address
# farmerDetails_contract_address = config.farmerDetails_contract_address
login_contract_address = config.login_contract_address 

# w3 = Web3(HTTPProvider("http://localhost:7545"))
# # IPC Provider error here
# eth = Web3(IPCProvider()).eth

# print(w3.isConnected())

# # Initialize a local account object from the private key of a valid Ethereum node address
# # Add your own private key here
local_acct = w3.eth.account.from_key(config.local_acct_key)

# # compile your smart contract with truffle first
# modify
# cropDetails_truffleFile = json.load(open('./build/contracts/CropDetails.json'))
# cropDetails_abi = cropDetails_truffleFile['abi']

# farmerDetails_truffleFile = json.load(open('./build/contracts/FarmerDetails.json'))
# farmerDetails_abi = farmerDetails_truffleFile['abi']

login_truffleFile = json.load(open('./build/contracts/Login.json'))
login_abi = login_truffleFile['abi']


# # Initialize a contract object with the smart contract compiled artifacts
# Modify
# cropDetails_contract_instance = w3.eth.contract(abi=cropDetails_abi, address=cropDetails_contract_address)
# farmerDetails_contract_instance = w3.eth.contract(abi=farmerDetails_abi, address=farmerDetails_contract_address)
login_contract_instance = w3.eth.contract(abi=login_abi, address=login_contract_address)

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
    txn_hash = login_contract_instance.functions.getUser(address).call()
    print(w3.eth.getTransactionReceipt(txn_hash))


@mod_fpc.route("/registerFPC",methods=["GET","POST"])
def registerFPC():
    #print(contract_address)
    #print(w3.isConnected())
    #print(request.form)
    if request.method == "POST":
        email = request.form.get('email') 
        password = request.form.get('password')
        #pwd_hash = hashlib.sha256(password.encode()).hexdigest()
        #addNewUser(email, pwd_hash, 'farmer')

        user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database

        if user: # if a user is found, we want to redirect back to signup page so user can try again
            return redirect(url_for('common.login'))

        acct = Account.create(password)
        print(acct.address)

        # create a new user with the form data. Hash the password so the plaintext version isn't saved.
        new_user = User(email=email,  password_hash=generate_password_hash(password, method='sha256'), address = acct.address, role = ROLE.FPC)

        # add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        print(email,password)

        fpc_name = request.form.get('fpc_name')
        director = request.form.get('director')
        reg_no = request.form.get('reg_no')
        capacity = request.form.get('capacity')
        location = request.form.get('location')

        fpc_data = {
            "fpc_name"  : fpc_name,
            "director" : director,
            "location" : location,
            "reg_no" : reg_no,
            "capacity" : capacity
        }

        print([(fpc, fpc_data[fpc]) for fpc in fpc_data])

        # @Vidhi Modify 
        # txn_dict = {
        #         'from': local_acct.address,
        #         'to': farmerDetails_contract_address,
        #         'value': '0',
        #         'gas': 2000000,
        #         'gasPrice': w3.toWei('40', 'gwei')
        #         }
        # farmer_address = acct.address
        # txn_hash = farmerDetails_contract_instance.functions.addFarmer(farmer_address,email,plot_owner,plot_number,plot_address,True).transact(txn_dict)
        # print(txn_hash)
        return redirect(url_for('common.login'))

    return render_template('registerFPC.html')

@mod_fpc.route("/fpcPage", methods=["GET","POST"])
@login_required
def fpcPage():
    if request.method=="POST":
        if 'fpcProfile' in request.form:
            return redirect(url_for('fpc.updateFpcProfile'))
        elif 'addTransaction' in request.form:
            return redirect(url_for('common.addTransactionDetails'))

    return render_template('FpcFunctions.html')

@mod_fpc.route("/updateFpcProfile", methods=["GET","POST"])
@login_required
def updateFpcProfile():
    # fpc_data = fpcDetails_contract_instance.functions.getFpc(current_user.address,i).call()
    if request.method == "POST":
        
        print("POST")       
        # txn_dict = {
        #         'from': local_acct.address,
        #         'to': farmerDetails_contract_address,
        #         'value': '0',
        #         'gas': 2000000,
        #         'gasPrice': w3.toWei('40', 'gwei')
        #         }
        # farmer_address = current_user.address

        if "update" in request.form:
            fpc_name = request.form.get('fpc_name')
            director = request.form.get('director')
            reg_no = request.form.get('reg_no')
            capacity = request.form.get('capacity')
            location = request.form.get('location')

            fpc_data = {
                "fpc_name"  : fpc_name,
                "director" : director,
                "location" : location,
                "reg_no" : reg_no,
                "capacity" : capacity
            }       
            # Integrate and update data with contract functions
            flash('Data Updated')
        elif "changePassword" in request.form:
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            user = User.query.filter_by(email=current_user.email).first()
            if not check_password_hash(user.password_hash, current_password):
                flash('Current Password does not match')

            else:
                user.password_hash = generate_password_hash(new_password, method='sha256')
                db.session.commit()
                flash('Password Updated Successfully')
        
    return render_template('updateFPC.html', current_user=current_user)