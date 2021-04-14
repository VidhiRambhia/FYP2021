import json
import sys
import datetime
import time
import hashlib
import os
from web3 import Web3, HTTPProvider, IPCProvider
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, Blueprint, render_template, request, redirect, url_for, flash
from flask_login import UserMixin, LoginManager, login_user, login_required, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from flaskapp.config import config
from flaskapp.models import User
from flaskapp import db, w3, eth, app
from flaskapp.Role import ROLE
import random
import string

mod_common = Blueprint('common', __name__, url_prefix='')

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

transactionDetails_contract_address = config.transactionDetails_contract_address
logisticsDetails_contract_address = config.logisticsDetails_contract_address
cropDetails_contract_address = config.cropDetails_contract_address

local_acct = w3.eth.account.from_key(config.local_acct_key)

transactionDetails_truffleFile = json.load(open('./build/contracts/TransactionDetails.json'))
transactionDetails_abi = transactionDetails_truffleFile['abi']
logisticsDetails_truffleFile = json.load(open('./build/contracts/LogisticsDetails.json'))
logisticsDetails_abi = logisticsDetails_truffleFile['abi']
cropDetails_truffleFile = json.load(open('./build/contracts/CropDetails.json'))
cropDetails_abi = cropDetails_truffleFile['abi']

transactionDetails_contract_instance = w3.eth.contract(abi=transactionDetails_abi, address=transactionDetails_contract_address)
logisticsDetails_contract_instance = w3.eth.contract(abi=logisticsDetails_abi, address=logisticsDetails_contract_address)
cropDetails_contract_instance = w3.eth.contract(abi=cropDetails_abi, address=cropDetails_contract_address)

@mod_common.route("/home")
@mod_common.route("/", methods=["GET", "POST"])
def index():
    if current_user:
        return render_template('home.html', current_user=current_user)
    return render_template('home.html')


@mod_common.route("/chooseRole", methods=["GET", "POST"])
def chooseRole():
    if(request.method == "POST"):
        selectedRole = request.form.get('role')
        print('selected role: ', selectedRole)
        if (selectedRole == 'farmer'):
            return redirect(url_for('farmer.registerFarmer'))
        if (selectedRole == 'fpc'):
            return redirect(url_for('fpc.registerFPC'))
        if (selectedRole == 'retailer'):
            return redirect(url_for('retailer.registerRetailer'))

    return render_template('ChooseRole.html')


@mod_common.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password_hash, password):
            print("Oops, wrong credentials.")
            flash('Please check your login details and try again.')
            return redirect(url_for('common.login'))

        login_user(user, remember=False)

        # Conditions for different entities
        print(current_user.role)
        if(current_user.role == 'FARMER'):
            return redirect(url_for('farmer.farmerPage'))
        elif(current_user.role == 'FPC'):
            return redirect(url_for('fpc.fpcPage'))
        elif(current_user.role == 'RETAIL_STORE'):
            return redirect(url_for('retailer.retailerPage'))
    return render_template("Login.html")


@mod_common.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/')


@mod_common.route("/error")
def error():
    return render_template('error.html')

@mod_common.route("/customer")
def customer():
    return render_template('customer.html')

@mod_common.route("/addTransactionDetails", methods=["GET", "POST"])
@login_required
def addTransactionDetails():
    sellers = []
    if current_user.role == 'FARMER':
        fpc_users = User.query.filter_by(role=ROLE.FPC).all()
        for fpc in fpc_users:
            seller = {
                "name":fpc.name,
                "address":fpc.address
            }
            sellers.append(seller)
        print(sellers)
    elif current_user.role == 'FPC':
        retailer_users = User.query.filter_by(role=ROLE.RETAIL_STORE).all()
        for retailer in retailer_users:
            seller = {
                "name":retailer.name,
                "address":retailer.address
            }
            sellers.append(seller)
        print(sellers)

    if request.method == 'POST':
        buyer_address = ""
        buyer_name = ""
        if request.form.get('buyer_name'):
            buyer_address = request.form.get('buyer_name')
            buyer_user = User.query.filter_by(address=buyer_address).first()
            buyer_name = buyer_user.name
        seller_name = current_user.name
        crop_name = request.form.get('crop_name')
        product_grade = request.form.get('product_grade')
        cost = int(request.form.get('cost'))
        quantity =  int(request.form.get('quantity'))
        crop_id = int(request.form.get('crop_id'))
        package_id = buyer_name[:2].upper() + seller_name[:2].upper() + str(random.randint(1, 100000))
        print(buyer_address)

        txn_dict = {
                'from': local_acct.address,
                'to': transactionDetails_contract_address,
                'value': '0',
                'gas': 2000000,
                'gasPrice': w3.toWei('40', 'gwei')
                }

        if current_user.role == ROLE.FARMER:
            print(request.form)
            txn_hash = transactionDetails_contract_instance.functions.f2hTransaction(current_user.address,buyer_address,package_id,seller_name,buyer_name,crop_id,crop_name,cost,quantity).transact(txn_dict)
            if txn_hash:
                update_txn_dict = {
                'from': local_acct.address,
                'to': cropDetails_contract_address,
                'value': '0',
                'gas': 2000000,
                'gasPrice': w3.toWei('40', 'gwei')
                }
                update_txn_hash = cropDetails_contract_instance.functions.setSold(crop_id,current_user.address).transact(update_txn_dict)
        
        elif current_user.role == ROLE.FPC:
            prev_package_id = request.form.get('prev_package_id')
            txn_hash = transactionDetails_contract_instance.functions.h2rTransaction(current_user.address,buyer_address,package_id,seller_name,buyer_name,crop_id,crop_name,product_grade,cost,quantity,prev_package_id).transact(txn_dict)
            print(txn_hash)

        elif current_user.role == ROLE.RETAIL_STORE:
            prev_package_id = request.form.get('prev_package_id')
            txn_hash = transactionDetails_contract_instance.functions.r2cTransaction(current_user.address,package_id,seller_name,crop_id,crop_name,cost,quantity,prev_package_id).transact(txn_dict)
            print(txn_hash)
           

        if 'next' in request.form:
            return redirect(url_for('common.logistics', package_id=package_id))
        return displayTransactions()    
             
    
    return render_template('addTransactionDetails.html', current_user=current_user, sellers=sellers)


@mod_common.route("/logistics", methods=["GET", "POST"])
@login_required
def logistics():
    package_id = request.args.get('package_id')
    if request.method == 'POST':
        vehicle_type = request.form.get('vehicle_type')
        vehicle_number = request.form.get('vehicle_number')
        driver_name = request.form.get('driver_name')
        driver_contact = int(request.form.get('driver_contact'))
        dispatch_date = request.form.get('dispatch_date')
        package_id = request.form.get('package_id')
        dispatch_date = datetime.datetime(*[int(item) for item in dispatch_date.split('-')])
        dispatch_date_int = int(dispatch_date.strftime('%Y%m%d'))
        #lid = datetime.datetime.now()
        #lid = int(lid.strftime('%Y%m%d'))

        txn_dict = {
                'from': local_acct.address,
                'to': logisticsDetails_contract_address,
                'value': '0',
                'gas': 2000000,
                'gasPrice': w3.toWei('40', 'gwei')
                }

        txn_hash = logisticsDetails_contract_instance.functions.addLogistic(package_id,vehicle_type,vehicle_number,driver_name,driver_contact,dispatch_date_int).transact(txn_dict)
        print(txn_hash)

        if txn_hash:
            return redirect(url_for('common.displayTransactions'))
            
        
    return render_template('logistics.html', package_id=package_id)


@mod_common.route("/displayTransactions", methods=["GET", "POST"])
@login_required
def displayTransactions():
    txnFilter = "all"
    transactionIds = transactionDetails_contract_instance.functions.getTransactions(current_user.address).call()
    txns = []
    for txnId in transactionIds:
        transactionDetails = transactionDetails_contract_instance.functions.getTxnEntityDetails(txnId).call()
        transactionCropDetails = transactionDetails_contract_instance.functions.getTxnCropDetails(txnId).call()
        prev_package_id = transactionDetails_contract_instance.functions.getPrevId(txnId).call()
        isActive = transactionDetails_contract_instance.functions.getActiveStatus(txnId).call()

        txn = {
            'txn_id': txnId,
            'seller_type':transactionDetails[0],
            'seller_name': transactionDetails[1],
            'buyer_type':transactionDetails[2],
            'buyer_name': transactionDetails[3],
            'crop_id': transactionCropDetails[0],
            'crop_name': transactionCropDetails[1],
            'grade': transactionCropDetails[2],
            'price' : transactionCropDetails[3],
            'quantity' : transactionCropDetails[4],
            'remaining_quantity': transactionCropDetails[5],
            'isActive': isActive,
            'vehicle_type': None,
            'vehicle_number':None,
            'driver_name':None,
            'driver_contact':None,
            'dispatch_date':None,

        }
        if transactionDetails[0] != 3:
            logisticsDetails = logisticsDetails_contract_instance.functions.getLog(txnId).call()
            dispatch_date = list(str(logisticsDetails[5]))
            dispatch_date = ''.join(dispatch_date[6:8]) + '-'  + ''.join(dispatch_date[4:6]) +  '-' + ''.join(dispatch_date[0:4]) 
            txn['vehicle_type'] = logisticsDetails[1]
            txn['vehicle_number']= logisticsDetails[2]
            txn['driver_name']= logisticsDetails[3]
            txn['driver_contact']= logisticsDetails[4]
            txn['dispatch_date']= dispatch_date

        print(txn)
        txns.append(txn)
    if request.method == "POST":
        txnFilter = request.form.get('txnFilter')
        if txnFilter == "bought":
            txnsFiltered = []
            for txn in txns:
                print(txn)
                if txn['buyer_name'] == current_user.name:
                    txnsFiltered.append(txn)
            return render_template('displayTransactions.html', current_user=current_user,txns=txnsFiltered,txnFilter=txnFilter)
        elif txnFilter == "sold":
            txnsFiltered = []
            for txn in txns:      
                if txn['seller_name'] == current_user.name:
                    txnsFiltered.append(txn)
            return render_template('displayTransactions.html', current_user=current_user,txns=txnsFiltered,txnFilter=txnFilter)

    return render_template('displayTransactions.html', current_user=current_user,txns=txns,txnFilter=txnFilter)

@mod_common.route("/tracking", methods=["GET", "POST"])
def tracking():
    txn_log = {}
    txn_log['cropDetails'] = {
        'cropName' : '',
        'cropGrade' : ''
    }

    txn_log['f2h'] = {
        'txn_id' : '',
        'dateOfTransaction' : '',
        'soldBy' : ''
    }

    txn_log['h2r'] = {
        'txn_id' : '',
        'dateOfTransaction' : '',
        'soldBy' : ''
    }

    txn_log['r2c'] = {
        'txn_id' : '',
        'price' : '',
        'quantity' : '',
        'soldBy' : ''
    }
    if request.method == 'POST':
        r2c_id = request.form.get('t_id')
        print(r2c_id)
        h2r_id = transactionDetails_contract_instance.functions.getPrevId(r2c_id).call()
        print(h2r_id)
        f2h_id = transactionDetails_contract_instance.functions.getPrevId(h2r_id).call()
        print(f2h_id)

        if(h2r_id =="" or f2h_id ==""):
            return render_template('404.html')
        # farmer side details
        f2h_logistics = logisticsDetails_contract_instance.functions.getLog(f2h_id).call()
        f2h_entities = transactionDetails_contract_instance.functions.getTxnEntityDetails(f2h_id).call()
        cropId = transactionDetails_contract_instance.functions.getTxnCropDetails(f2h_id).call()[0]
        cropDetailsFarmer = cropDetails_contract_instance.functions.getCrop2(f2h_entities[4], cropId).call()
        # print(cropDetailsFarmer)

        # fpc side details
        h2r_logistics = logisticsDetails_contract_instance.functions.getLog(h2r_id).call()
        h2r_entities = transactionDetails_contract_instance.functions.getTxnEntityDetails(h2r_id).call()
        cropDetails = transactionDetails_contract_instance.functions.getTxnCropDetails(h2r_id).call()

        # retailer side details
        r2c_crop = transactionDetails_contract_instance.functions.getTxnCropDetails(r2c_id).call()
        r2c_entities = transactionDetails_contract_instance.functions.getTxnEntityDetails(r2c_id).call()
        
        txn_log['cropDetails'] = {
            'cropName' : cropDetails[1],
            'cropGrade' : cropDetails[2],
            'fertilizerUsed' : cropDetailsFarmer[0],
            'sowingDate' : str(cropDetailsFarmer[2])[:4] + '-' + str(cropDetailsFarmer[2])[4:6] + '-' + str(cropDetailsFarmer[2])[6:],
            'harvestDate' : str(cropDetailsFarmer[3])[:4] + '-' + str(cropDetailsFarmer[3])[4:6] + '-' + str(cropDetailsFarmer[3])[6:],  
        }

        txn_log['f2h'] = {
            'txn_id' : f2h_id,
            'dateOfTransaction' : str(f2h_logistics[5])[:4] + '-' + str(f2h_logistics[5])[4:6] + '-' + str(f2h_logistics[5])[6:],
            'soldBy' : f2h_entities[1],
            'vehicleType' : f2h_logistics[1]
        }

        txn_log['h2r'] = {
            'txn_id' : h2r_id,
            'dateOfTransaction' : str(h2r_logistics[5])[:4] + '-' + str(h2r_logistics[5])[4:6] + '-' + str(h2r_logistics[5])[6:],
            'soldBy' : h2r_entities[1],
            'vehicleType' : h2r_logistics[1]
        }

        txn_log['r2c'] = {
            'txn_id' : r2c_id,
            'price' : r2c_crop[3],
            'quantity' : r2c_crop[4],
            'soldBy' : r2c_entities[1]
        }
        #print(txn_log)
    #time.sleep(10)
    return render_template('customer.html', txn_log= txn_log)
