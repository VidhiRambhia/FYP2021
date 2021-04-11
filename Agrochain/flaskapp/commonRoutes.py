import json
import sys
import datetime
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

local_acct = w3.eth.account.from_key(config.local_acct_key)

transactionDetails_truffleFile = json.load(open('./build/contracts/TransactionDetails.json'))
transactionDetails_abi = transactionDetails_truffleFile['abi']
logisticsDetails_truffleFile = json.load(open('./build/contracts/LogisticsDetails.json'))
logisticsDetails_abi = logisticsDetails_truffleFile['abi']

transactionDetails_contract_instance = w3.eth.contract(abi=transactionDetails_abi, address=transactionDetails_contract_address)
logisticsDetails_contract_instance = w3.eth.contract(abi=logisticsDetails_abi, address=logisticsDetails_contract_address)

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
        # if (selectedRole == 'retailer'):
        #     return redirect(url_for('retailer.registerRetailer'))

    return render_template('ChooseRole.html')


@mod_common.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":

        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password_hash, password):
            print("hi")
            flash('Please check your login details and try again.')
            return redirect(url_for('common.login'))

        login_user(user, remember=False)

        # Conditions for different entities
        if(current_user.role == 'FARMER'):
            return redirect(url_for('farmer.farmerPage'))
        elif(current_user.role == 'FPC'):
            return redirect(url_for('fpc.fpcPage'))
        # elif(current_user.role == 'RETAILER'):
        #     return redirect(url_for('retailer.retailerPage'))
    return render_template("Login.html")


@mod_common.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/')


@mod_common.route("/error")
def error():
    return render_template('error.html')

@mod_common.route("/retailerPage")
def retailerpage():
    return render_template('retailerFunctions.html')

@mod_common.route("/registerRetailer")
def reg():
    return render_template('registerRetailer.html')

@mod_common.route("/updateRetailer")
def update():
    return render_template('updateRetailer.html')

@mod_common.route("/addTransactionDetails", methods=["GET", "POST"])
@login_required
def addTransactionDetails():
    if request.method == 'POST':
        buyer_name = request.form.get('buyer_name')
        seller_name = request.form.get('seller_name')
        crop_name = request.form.get('crop_name')
        product_grade = request.form.get('product_grade')
        cost = int(request.form.get('cost'))
        quantity =  int(request.form.get('quantity'))
        package_id = buyer_name[:2].upper() + seller_name[:2].upper() + str(random.randint(1, 100000))
        print(package_id)
        tid = datetime.datetime.now()
        tid = int(tid.strftime('%Y%m%d'))

        txn_dict = {
                'from': local_acct.address,
                'to': transactionDetails_contract_address,
                'value': '0',
                'gas': 2000000,
                'gasPrice': w3.toWei('40', 'gwei')
                }


        if current_user.role == ROLE.FARMER:
            txn_hash = transactionDetails_contract_instance.functions.f2hTransaction(tid,seller_name,buyer_name,crop_name,cost,quantity,0).transact(txn_dict)
            print(txn_hash)
        
        elif current_user.role == ROLE.FPC:
            txn_hash = transactionDetails_contract_instance.functions.h2rTransaction(tid,seller_name,buyer_name,crop_name,product_grade,cost,quantity,package_id,0,"").transact(txn_dict)
            print(txn_hash)
            

        if 'next' in request.form:
            return redirect(url_for('common.logistics', package_id=package_id))
    
    return render_template('addTransactionDetails.html', current_user=current_user)


@mod_common.route("/logistics", methods=["GET", "POST"])
@login_required
def logistics():
    package_id = request.args.get('package_id')
    print(package_id)
    if request.method == 'POST':
        vehicle_type = request.form.get('vehicle_type')
        vehicle_number = request.form.get('vehicle_number')
        driver_name = request.form.get('driver_name')
        driver_contact = int(request.form.get('driver_contact'))
        dispatch_date = request.form.get('dispatch_date')
        dispatch_date = datetime.datetime(*[int(item) for item in dispatch_date.split('-')])
        dispatch_date_int = int(dispatch_date.strftime('%Y%m%d'))
        lid = datetime.datetime.now()
        lid = int(lid.strftime('%Y%m%d'))

        txn_dict = {
                'from': local_acct.address,
                'to': logisticsDetails_contract_address,
                'value': '0',
                'gas': 2000000,
                'gasPrice': w3.toWei('40', 'gwei')
                }

        txn_hash = logisticsDetails_contract_instance.functions.addLogistic(lid,vehicle_type,vehicle_number,driver_name,driver_contact,dispatch_date_int).transact(txn_dict)
        print(txn_hash)
        
    return render_template('logistics.html', package_id=package_id)
