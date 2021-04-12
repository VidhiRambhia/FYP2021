import json
import sys
import datetime
import hashlib
import os
import time
from web3 import Web3, HTTPProvider, IPCProvider
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, Blueprint, render_template, request, redirect, url_for, flash
from flask_login import UserMixin, LoginManager, login_user, login_required, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from flaskapp.config import config
from flaskapp.models import User
from flaskapp import db, w3, eth, app
from flaskapp.Role import ROLE
from eth_account import Account

mod_retailer = Blueprint('retailer', __name__, url_prefix='')

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

retailerDetails_contract_address = config.retailerDetails_contract_address

local_acct = w3.eth.account.from_key(config.local_acct_key)

retailerDetails_truffleFile = json.load(open('./build/contracts/RetailerDetails.json'))
retailerDetails_abi = retailerDetails_truffleFile['abi']

retailerDetails_contract_instance = w3.eth.contract(abi=retailerDetails_abi, address=retailerDetails_contract_address)

@mod_retailer.route("/registerRetailer", methods=["GET", "POST"])
def registerRetailer():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        retailer_name = request.form.get('retailer_name')
        user = User.query.filter_by(email=email).first()

        if user:
            print("user exists")
            return redirect(url_for('common.login'))

        acct = Account.create(password)
        print(acct.address)

        new_user = User(email=email,name=retailer_name, password_hash=generate_password_hash(password, method='sha256'), address=acct.address, role=ROLE.RETAIL_STORE)

        print(new_user)

        retailer_name = request.form.get('retailer_name')
        reg_no = request.form.get('reg_number')
        location = request.form.get('location')
        city = request.form.get('city')
        retailer_address = acct.address

        # retailer_data = {
        #     "retailer_name"  : retailer_name,
        #     "city" : city,
        #     "location" : location,
        #     "reg_no" : reg_no
        # }

        # print([(retailer, retailer_data[retailer]) for retailer in retailer_data])


        txn_dict = {
                'from': local_acct.address,
                'to': retailerDetails_contract_address,
                'value': '0',
                'gas': 2000000,
                'gasPrice': w3.toWei('40', 'gwei')
                }

        txn_hash = retailerDetails_contract_instance.functions.addRetailer(retailer_address, retailer_name, location, city, reg_no).transact(txn_dict)
        print(txn_hash)
        if txn_hash:
            db.session.add(new_user)
            db.session.commit()

        return redirect(url_for('common.login'))

    return render_template('registerRetailer.html')


@mod_retailer.route("/retailerPage", methods=["GET", "POST"])
@login_required
def retailerPage():
    if request.method == "POST":
        if 'retailerProfile' in request.form:
            return redirect(url_for('retailer.updateRetailerProfile'))
        elif 'addTransaction' in request.form:
            return redirect(url_for('retailer.addRetailTransactionDetails'))

    return render_template('retailerFunctions.html')


@mod_retailer.route("/updateRetailerProfile", methods=["GET", "POST"])
@login_required
def updateRetailerProfile():
    retailer_data = retailerDetails_contract_instance.functions.getRetailer(current_user.address).call()
    retailer_data = {
            "retailer_name"  : retailer_data[0],
            "location" : retailer_data[1],
            "city" : retailer_data[2],
            "reg_no" : retailer_data[3],
        }
    print(retailer_data)
    if request.method == "POST":
        print("POST")       
        txn_dict = {
                'from': local_acct.address,
                'to': retailerDetails_contract_address,
                'value': '0',
                'gas': 2000000,
                'gasPrice': w3.toWei('40', 'gwei')
                }
        retailer_address = current_user.address    

        if "update" in request.form:
            retailer_name = request.form.get('retailer_name')
            reg_no = request.form.get('reg_number')
            city = request.form.get('city')
            location = request.form.get('location')

            txn_hash = retailerDetails_contract_instance.functions.updateRetailer(retailer_address,retailer_name,location,city,reg_no).transact(txn_dict)

            retailer_data = {
                "retailer_name"  : retailer_name,
                "location" : location,
                "city" : city,
                "reg_no" : reg_no
            }

            flash('Profile Updated')

        elif "changePassword" in request.form:
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            user = User.query.filter_by(email=current_user.email).first()
            if not check_password_hash(user.password_hash, current_password):
                flash('Current Password does not match')

            else:
                user.password_hash = generate_password_hash(
                    new_password, method='sha256')
                db.session.commit()
                flash('Password Updated Successfully')
    return render_template('updateRetailer.html', current_user=current_user, retailer_data=retailer_data)

@mod_retailer.route("/addRetailTransactionDetails", methods=["GET", "POST"])
@login_required
def addRetailTransactionDetails():
    if request.method == 'POST':
        sell_date = request.form.get('sell_date')
        sell_date = datetime.datetime(*[int(item) for item in sell_date.split('-')])
        sell_date_int = int(sell_date.strftime('%Y%m%d'))
        cost = request.form.get('cost')
        quantity = request.form.get('quantity')
        print(cost)
    return render_template('addTransactionDetails.html', current_user=current_user)
