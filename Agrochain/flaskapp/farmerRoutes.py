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

mod_farmer = Blueprint('farmer', __name__, url_prefix='')

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#db.create_all()

cropDetails_contract_address = config.cropDetails_contract_address
farmerDetails_contract_address = config.farmerDetails_contract_address
login_contract_address = config.login_contract_address 

# w3 = Web3(HTTPProvider("http://localhost:7545"))
# # IPC Provider error here
# eth = Web3(IPCProvider()).eth

# print(w3.isConnected())

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


@mod_farmer.route("/registerFarmer",methods=["GET","POST"])
def registerFarmer():
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
        new_user = User(email=email,  password_hash=generate_password_hash(password, method='sha256'), address = acct.address, role = ROLE.FARMER)

        # add the new user to the database
        db.session.add(new_user)
        db.session.commit()

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
        farmer_address = acct.address
        txn_hash = farmerDetails_contract_instance.functions.addFarmer(farmer_address,email,plot_owner,plot_number,plot_address,True).transact(txn_dict)
        print(txn_hash)

        if request.form.get('plot_number_1'):
            plot_number_1 = request.form.get('plot_number_1')
            plot_owner_1 = request.form.get('plot_owner_1')
            plot_address_1 = request.form.get('plot_address_1')
            txn_hash = farmerDetails_contract_instance.functions.addPlot(farmer_address,plot_owner_1,plot_number_1,plot_address_1).transact(txn_dict)
            print(txn_hash)
        if request.form.get('plot_number_2'):
            plot_number_2 = request.form.get('plot_number_2')
            plot_owner_2 = request.form.get('plot_owner_2')
            plot_address_2 = request.form.get('plot_address_2')
            txn_hash = farmerDetails_contract_instance.functions.addPlot(farmer_address,plot_owner_2,plot_number_2,plot_address_2).transact(txn_dict)
            print(txn_hash)

    return render_template('registerFarmer.html')


@mod_farmer.route("/addCropDetails",methods=["GET","POST"])
@login_required
def addCropDetails():
    crop_id  = request.args.get('crop_id')
    crop = None
    if crop_id:
        cropData = cropDetails_contract_instance.functions.crops(current_user.address,int(crop_id)).call()
        crop_sowing_date = list(str(cropData[6]))
        crop_harvesting_date = list(str(cropData[7]))
        crop_sowing_date =  ''.join(crop_sowing_date[0:4]) + '-' + ''.join(crop_sowing_date[4:6]) +  '-' + ''.join(crop_sowing_date[6:8])
        crop_harvesting_date = ''.join(crop_harvesting_date[0:4]) + '-' +  ''.join(crop_harvesting_date[4:6])+ '-' +  ''.join(crop_harvesting_date[6:8])  
        crop = {
            "crop_id": cropData[0],
            "crop_type": cropData[1],
            "crop_name":cropData[2],
            "crop_fertilizer":cropData[3],
            "crop_source_tag_number":cropData[4],
            "crop_quantity": cropData[5],
            "crop_sowing_date" : crop_sowing_date,
            "crop_harvesting_date": crop_harvesting_date
        }
    print(crop)
    if request.method=="POST":
        if crop_id:
            quantity = int(request.form.get('quantity'))
            harvesting_date = request.form.get('harvesting_date')
            harvesting_date = datetime.datetime(*[int(item) for item in harvesting_date.split('-')])
            harvesting_date_int = int(harvesting_date.strftime('%Y%m%d'))
            txn_dict = {
                    'from': local_acct.address,
                    'to': cropDetails_contract_address,
                    'value': '0',
                    'gas': 3000000,
                    'gasPrice': w3.toWei('40', 'gwei')
                    }
            txn_hash = cropDetails_contract_instance.functions.updateCrop(int(crop_id),current_user.address,harvesting_date_int,quantity).transact(txn_dict)
            return render_template('addCropDetails.html',current_user=current_user,crop=crop)
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
        farmer_address = current_user.address #get address
        sowing_date = datetime.datetime(*[int(item) for item in sowing_date.split('-')])
        sowing_date_int = int(sowing_date.strftime('%Y%m%d'))
        harvesting_date = datetime.datetime(*[int(item) for item in harvesting_date.split('-')])
        harvesting_date_int = int(harvesting_date.strftime('%Y%m%d'))
        crop_id = cropDetails_contract_instance.functions.addCrop1(crop_type,crop_name,source_tag_number,current_user.address).call()
        txn_hash = cropDetails_contract_instance.functions.addCrop1(crop_type,crop_name,source_tag_number,current_user.address).transact(txn_dict)
        txn_hash = cropDetails_contract_instance.functions.addCrop2(int(crop_id),fertilizer,quantity,sowing_date_int,harvesting_date_int, current_user.address).transact(txn_dict)
        #print(txn_hash)
        print(crop_id)
    return render_template('addCropDetails.html',current_user=current_user,crop=crop)

@mod_farmer.route("/farmerPage", methods=["GET","POST"])
@login_required
def farmerPage():
    if request.method=="POST":
        if 'profile' in request.form:
            return redirect(url_for('farmer.updateFarmerProfile'))
        elif 'addCrop' in request.form:
            return redirect(url_for('farmer.addCropDetails'))
        elif 'updateCrop' in request.form:
            return redirect(url_for('farmer.getCrops'))

    return render_template('FarmerFunctions.html')



@mod_farmer.route("/updateFarmerProfile", methods=["GET","POST"])
@login_required
def updateFarmerProfile():
    i = 0
    plots = []
    while True:
        try:
            farmerData = farmerDetails_contract_instance.functions.getFarmer(current_user.address,i).call()
            plot = {"plot_owner" : farmerData[1],
                "plot_number" : farmerData[2],
                "plot_address" : farmerData[3]}
            plots.append(plot)
            i = i+1
        except :
            break
    print(plots)
    if request.method == "POST":
        print("POST")        
        txn_dict = {
                'from': local_acct.address,
                'to': farmerDetails_contract_address,
                'value': '0',
                'gas': 2000000,
                'gasPrice': w3.toWei('40', 'gwei')
                }
        farmer_address = current_user.address
        if 'update' in request.form:
            print('here')
            txn_hash = farmerDetails_contract_instance.functions.deletePlot(farmer_address).transact(txn_dict)
            print(txn_hash)
            i = 0
            while True:
                try:
                    if(request.form.get('plot_number_' + str(i)) == ""):
                        break
                    plot_number = request.form.get('plot_number_' + str(i))
                    # print(plot_number)
                    plot_owner = request.form.get('plot_owner_' + str(i))
                    # print(plot_owner)
                    plot_address = request.form.get('plot_address_' + str(i))
                    # print(plot_address)
                    txn_hash = farmerDetails_contract_instance.functions.addPlot(farmer_address,plot_owner,plot_number,plot_address).transact(txn_dict)
                    print(txn_hash)
                    i = i + 1
                except :
                    break
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

        
    return render_template('updateFarmer.html', current_user=current_user,plots=plots) 

@mod_farmer.route("/getCrops", methods=["GET","POST"])
@login_required
def getCrops():
    i = 0
    crops = []
    while True:
        try:
            cropData = cropDetails_contract_instance.functions.crops(current_user.address,i).call()
            crop_sowing_date = list(str(cropData[6]))
            crop_harvesting_date = list(str(cropData[7]))
            crop_sowing_date = ''.join(crop_sowing_date[6:8]) + '-'  + ''.join(crop_sowing_date[4:6]) +  '-' + ''.join(crop_sowing_date[0:4]) 
            crop_harvesting_date = ''.join(crop_harvesting_date[6:8]) + '-'  + ''.join(crop_harvesting_date[4:6]) +  '-' + ''.join(crop_harvesting_date[0:4])
            crop = {
                "crop_id": cropData[0],
                "crop_type": cropData[1],
                "crop_name":cropData[2],
                "crop_fertilizer":cropData[3],
                "crop_source_tag_number":cropData[4],
                "crop_quantity": cropData[5],
                "crop_sowing_date" : crop_sowing_date,
                "crop_harvesting_date": crop_harvesting_date
            }
            crops.append(crop)
            i = i+1
        except :
            break

    print(crops)
    return render_template('displayCrops.html', current_user=current_user,crops=crops) #Add html page



