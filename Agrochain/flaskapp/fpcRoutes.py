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

fpcDetails_contract_address = config.fpcDetails_contract_address

local_acct = w3.eth.account.from_key(config.local_acct_key)

fpcDetails_truffleFile = json.load(open('./build/contracts/FpcDetails.json'))
fpcDetails_abi = fpcDetails_truffleFile['abi']

fpcDetails_contract_instance = w3.eth.contract(abi=fpcDetails_abi, address=fpcDetails_contract_address)

@mod_fpc.route("/registerFPC",methods=["GET","POST"])
def registerFPC():
    if request.method == "POST":
        email = request.form.get('email') 
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first() 

        if user:
            return redirect(url_for('common.login'))

        acct = Account.create(password)
        print(acct.address)

        new_user = User(email=email,  password_hash=generate_password_hash(password, method='sha256'), address = acct.address, role = ROLE.FPC)

        fpc_name = request.form.get('fpc_name')
        director = request.form.get('director')
        reg_no = request.form.get('reg_number')
        capacity = int(request.form.get('capacity'))
        location = request.form.get('location')
        fpc_address = acct.address

        print(location)

        # fpc_data = {
        #     "fpc_name"  : fpc_name,
        #     "director" : director,
        #     "location" : location,
        #     "reg_no" : reg_no,
        #     "capacity" : capacity
        # }

        # print([(fpc, fpc_data[fpc]) for fpc in fpc_data])

        txn_dict = {
                'from': local_acct.address,
                'to': fpcDetails_contract_address,
                'value': '0',
                'gas': 2000000,
                'gasPrice': w3.toWei('40', 'gwei')
                }
        fpc_address = acct.address
        txn_hash = fpcDetails_contract_instance.functions.addFpc(fpc_address,fpc_name,director,location,reg_no,capacity).transact(txn_dict)
        print(txn_hash)
        if txn_hash:
            db.session.add(new_user)
            db.session.commit()

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
    fpc_data = fpcDetails_contract_instance.functions.getFpc(current_user.address).call()
    fpc_data = {
            "fpc_name"  : fpc_data[0],
            "director" : fpc_data[1],
            "location" : fpc_data[2],
            "reg_no" : fpc_data[3],
            "capacity" : fpc_data[4]
        }
    print(fpc_data)
    if request.method == "POST":
        
        print("POST")       
        txn_dict = {
                'from': local_acct.address,
                'to': fpcDetails_contract_address,
                'value': '0',
                'gas': 2000000,
                'gasPrice': w3.toWei('40', 'gwei')
                }
        fpc_address = current_user.address
        if "update" in request.form:
            fpc_name = request.form.get('fpc_name')
            director = request.form.get('director')
            reg_no = request.form.get('reg_number')
            capacity = int(request.form.get('capacity'))
            location = request.form.get('location') 

            txn_hash = fpcDetails_contract_instance.functions.updateFpc(fpc_address,fpc_name,director,location,reg_no,capacity).transact(txn_dict)

            fpc_data = {
                "fpc_name"  : fpc_name,
                "director" : director,
                "location" : location,
                "reg_no" : reg_no,
                "capacity" : capacity
            }
            
            flash('Profile Updated')

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
        
    return render_template('updateFPC.html', current_user=current_user, fpc_data=fpc_data)