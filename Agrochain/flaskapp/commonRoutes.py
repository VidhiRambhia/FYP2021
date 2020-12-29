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

mod_common = Blueprint('common', __name__, url_prefix='')

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@mod_common.route("/home")
@mod_common.route("/", methods=["GET","POST"])
def index():
    if(request.method == "POST"):
        return redirect(url_for('common.login'))
    email = request.form.get('email') #Todo: Add other fields
    return render_template('home.html')



@mod_common.route("/chooseRole", methods=["GET","POST"])
def chooseRole():
    if(request.method=="POST"):
        selectedRole = request.form.get('role')
        print('selected role: ', selectedRole)
        if (selectedRole == 'farmer'):
            return redirect(url_for('farmer.registerFarmer'))

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



