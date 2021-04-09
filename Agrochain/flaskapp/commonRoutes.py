import json
import sys
import datetime
import hashlib
import os
from web3 import Web3, HTTPProvider,IPCProvider
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask,Blueprint, render_template, request, redirect, url_for,flash
from flask_login import UserMixin, LoginManager, login_user, login_required, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from flaskapp.config import config
from flaskapp.models import User
from flaskapp import db,w3,eth,app
import random

mod_common = Blueprint('common', __name__, url_prefix='')

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@mod_common.route("/home")
@mod_common.route("/", methods=["GET","POST"])
def index():
    if current_user:
        return render_template('home.html',current_user=current_user)
    return render_template('home.html')



@mod_common.route("/chooseRole", methods=["GET","POST"])
def chooseRole():
    if(request.method=="POST"):
        selectedRole = request.form.get('role')
        print('selected role: ', selectedRole)
        if (selectedRole == 'farmer'):
            return redirect(url_for('farmer.registerFarmer'))
        if (selectedRole == 'fpc'):
            return redirect(url_for('fpc.registerFPC'))

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
        return redirect(url_for('farmer.farmerPage'))

    return render_template("Login.html")

@mod_common.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/')


@mod_common.route("/error")
def error():
    return render_template('error.html')

@mod_common.route("/addTransactionDetails",methods=["GET","POST"])
@login_required
def addTransactionDetails():
    buyer_name = request.form.get('buyer_name')
    seller_name = request.form.get('seller_name')
    crop_name = request.form.get('crop_name')
    product_grade = request.form.get('product_grade')
    cost = float(request.form.get('cost'))
    quantity = request.form.get('quantity')
    package_id = buyer_name[:2] + seller_name[:2] + str(randint())
    #logistic id
    #prev_hash

    #connect with SC
    return render_template('addTransactionDetails.html',current_user=current_user,transaction=transaction)

@mod_common.route("/logistics", methods=["GET","POST"])
@login_required
def logistics():
    if request.method == 'POST': 
        vehicle_type = request.form.get('vehicle_type')
        l_id = request.form.get('l_id')
        vehicle_number = request.form.get('vehicle_number')
        driver_name = request.form.get('driver_name')
        driver_contact = request.form.get('driver_contact')
        dispatch_date = request.form.get('dispatch_date')
        dispatch_date = datetime.datetime(*[int(item) for item in dispatch_date.split('-')])
        dispatch_date_int = int(date_dispatched.strftime('%Y%m%d'))
        print(dispatch_date)
        # Connect with SC
    return render_template('logistics.html')