# Import flask and template operators
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from web3 import Web3, HTTPProvider,IPCProvider
import os
# Define the WSGI application object
app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['SECRET_KEY'] = 'secret-key-goes-here'
db = SQLAlchemy(app)
#db.create_all()

w3 = Web3(HTTPProvider("http://localhost:7545"))

eth = Web3(IPCProvider()).eth

print(w3.isConnected())


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


from flaskapp.farmerRoutes import mod_farmer
from flaskapp.commonRoutes import mod_common
from flaskapp.fpcRoutes import mod_fpc
from flaskapp.models import User

app.register_blueprint(mod_farmer)
app.register_blueprint(mod_common)
app.register_blueprint(mod_fpc)

db.create_all()
