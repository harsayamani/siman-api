from urllib import response
from flask import Flask
from flask_cors import CORS
from flask_httpauth import HTTPBasicAuth
from bin.helpers.db.mysqldb import MYSQLDB
from bin.modules.partners import PartnerHandler
from bin.modules.simanneal import SimannealHandler
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import bin.helpers.responses.data as data_response
import os

load_dotenv('.env')

app = Flask(__name__)
CORS(app)
auth = HTTPBasicAuth()

user = os.environ.get('BASIC_USERNAME')
pw = os.environ.get('BASIC_PASSWORD')
users = {
    user: generate_password_hash(pw)
}

@auth.verify_password
def verify_password(username, password):
    if username in users:
        return check_password_hash(users.get(username), password)
    return False

#define db
mysql = MYSQLDB(app)

# define handlers
partners_handler = PartnerHandler(mysql)
simanneal_handler = SimannealHandler(mysql)

#init main
main = app

#init route
@main.route('/')
def init():
    return data_response.data({}, 'Service Running Properly')

# partners route
@main.route('/api/v1/partner/get-all-partner')
@auth.login_required
def get_all_partners():
    return partners_handler.get_all_partner()

# simanneal route
@main.route('/api/v1/simanneal/run', methods=['POST'])
@auth.login_required
def run_simanneal():
    return simanneal_handler.run_simanneal()

if __name__ == "__main__":
    app.run(debug=True)
