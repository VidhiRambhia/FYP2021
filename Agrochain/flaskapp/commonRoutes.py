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
import random
import string

mod_common = Blueprint('common', __name__, url_prefix='')

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


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
        cost = request.form.get('cost')
        quantity = request.form.get('quantity')
        package_id = buyer_name[:2].upper(
        ) + seller_name[:2].upper() + str(random.randint(1, 100000))
        print(package_id)
    if 'next' in request.form:
        return redirect(url_for('common.logistics', package_id=package_id))
    # connect with SC
    return render_template('addTransactionDetails.html', current_user=current_user)


@mod_common.route("/logistics", methods=["GET", "POST"])
@login_required
def logistics():
    package_id = request.args.get('package_id')
    print(package_id)
    if request.method == 'POST':
        vehicle_type = request.form.get('vehicle_type')
        l_id = request.form.get('l_id')
        vehicle_number = request.form.get('vehicle_number')
        driver_name = request.form.get('driver_name')
        driver_contact = request.form.get('driver_contact')
        dispatch_date = request.form.get('dispatch_date')
        dispatch_date = datetime.datetime(
            *[int(item) for item in dispatch_date.split('-')])
        dispatch_date_int = int(dispatch_date.strftime('%Y%m%d'))
        # Connect with SC
    return render_template('logistics.html', package_id=package_id)
