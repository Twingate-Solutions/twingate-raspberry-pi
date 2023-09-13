# requires flask
# requires nmap (system) and python-namp
# requires wtforms
# Flask-WTF
# pip install bootstrap-flask
# pip install python-nmap (as sudo for OS fingerprinting)
# run with sudo flask --app server run -h 127.0.0.1 -p 10064 (sudo required because installing a Connector requires it)

from flask import Flask, request, render_template, url_for, flash, redirect
from wtforms import Form, TextAreaField, validators, StringField, SubmitField
from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap5

from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError

import sys,re

# internal library imports
sys.path.insert(1, './libs')
import storage
import errors
import network
import connectors
import resources
import rn

app = Flask(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d233f2b6176a'
REMOTE_NETWORK_NAME = "Customer Network"
CONNECTOR_NAME_STUB = "Twingate Box"
NETWORK_LOCATION = "ON_PREMISE"
SUBNET_NAME = "Customer Subnet"


bootstrap = Bootstrap5(app)
csrf = CSRFProtect(app)

ADMINCONSOLEREGEX = "https:[\/]{2}(.+)\.twingate\.com.*"

class TGInfoForm(FlaskForm):

    adminconsole_url = StringField('Admin Console URL (for example: https:///<yourtenantname>.twingate.com/)', validators=[DataRequired()])
    apitoken = StringField('Twingate API Token with Read, Write & Provision permissions:', validators=[DataRequired(), Length(134, 134)])
    #adminconsole_url = StringField('Admin Console URL (for example: https:///<yourtenantname>.twingate.com/)', validators=[])
    #apitoken = StringField('Twingate API Token with Read, Write & Provision permissions:', validators=[])
    submit = SubmitField('Submit')

    def validate_adminconsole_url(form, adminconsole_url):
        result = re.match(ADMINCONSOLEREGEX, adminconsole_url.data)
        if not result:
            raise ValidationError('Admin Console URL provided does not seem to be in the right format: https://<yourtenantname>.twingate.com/')

@app.route('/', methods=['GET', 'POST'])
def index():
    form = TGInfoForm()
    message = ""
    if form.validate_on_submit():

        adminurl = form.adminconsole_url.data
        token = form.apitoken.data
        tenant = re.match(ADMINCONSOLEREGEX, adminurl).group(1)
        print("Form validated:"+tenant)

            
        # storing info locally
        if not storage.is_token_valid(token):
                print(errors.wrong_token_format())
                return render_template('error.html',message = errors.rwrong_token_format())
                
        else:
             print("info stored locally.")
            
        storage.StoreTenant(tenant)
        storage.StoreAuthToken(token,tenant)
        # creates a temporary remote network
        HasError,resRN = rn.create_rn("TODELETE","ON_PREMISE")
        if HasError:
             print(errors.token_wrong_scope("READ or READ,WRITE only"))
             return render_template('error.html',message = errors.rtoken_wrong_scope("READ or READ,WRITE only"))
        else:
             print("API Token scope verified.")

        rn_id = resRN['data']['remoteNetworkCreate']['entity']['id']
        print("temporary RN ID:"+str(rn_id))
        # creates a temporary Connector
        HasError,resCONN = connectors.create_connector("TODELETE",rn_id)
        if HasError:
            rn.delete_rn(rn_id)
            print(errors.token_wrong_scope("READ or READ,WRITE only"))
            return render_template('error.html',message = errors.rtoken_wrong_scope("READ or READ,WRITE only"))
        else:
             print("temporary Connector info:"+str(resCONN))
        conn_id = resCONN['data']['connectorCreate']['entity']['id']
        print("temporary Connector ID:"+str(conn_id))
        HasError,payload = connectors.generate_tokens(conn_id)
        if HasError:
            rn.delete_rn(rn_id)
            print(errors.token_wrong_scope("READ or READ,WRITE only"))
            return render_template('error.html',message = errors.rtoken_wrong_scope("READ or READ,WRITE only"))
        else:
             print("temp Connector tokens generated.")
        rn.delete_rn(rn_id)
        print("temp RN removed.")
        HasError,resp = rn.create_home_rn(REMOTE_NETWORK_NAME,NETWORK_LOCATION)
        if HasError:
            print(errors.connector_creation(connector_info))
            return render_template('error.html',message = errors.rconnector_creation(connector_info))
        else:
             print("Remote Network created.")
        rn_id = resp['id']
        print("Remote Network ID:"+str(rn_id))
        HasError,connector_info = connectors.create_home_connector(CONNECTOR_NAME_STUB,rn_id)
        if HasError:
            print(errors.connector_creation(connector_info))
            return render_template('error.html',message = errors.rconnector_creation(connector_info))
        else:
            print("Home Connector created.")
        connector_id = connector_info['data']['connectorCreate']['entity']['id']
        HasError,payload = connectors.generate_tokens(connector_id)
        # Connector tokens are never required client side as they are stored in a staged install script
        if HasError:
            # should we delete the home remote network here?
            print(errors.token_creation(payload))
            return render_template('error.html',message = errors.rtoken_creation(payload))
        else:
             print("Home Connector tokens created.")

        hasError,resp = connectors.install_connector()
        if hasError:
            print(errors.rconnector_install_error(resp))
            return render_template('error.html',message = errors.rconnector_install_error(resp))
        else:
             print("Home Connector installed.")
        subnet = network.get_subnet()
        print("Subnet retrieved:"+str(subnet))
        hasError,msg = resources.create_resource_in_homenetwork(rn_id,str(subnet),SUBNET_NAME)
        if hasError:
            print(errors.tg_res_creation_error(msg))
            return render_template('error.html',message = errors.rtg_res_creation_error(msg))
        else:
            print(errors.success())
            return render_template('success.html')
            
        
    return render_template('index.html', form=form, message=message)

# stores tenant name and API token locally
@app.route("/tenant", methods=['POST'])
def store_tenant():
    if request.method == 'POST':
        content_type = request.headers.get('Content-Type')
        if (content_type == 'application/json'):
            json = request.json
            if not json['tenant']:
                return errors.token_or_tenant_missing("tenant name")
            if not json ['token']:
                return errors.token_or_tenant_missing("API token")

            tenant = json['tenant']
            token = json['token']
            if not storage.is_token_valid(token):
                return errors.wrong_token_format()
            
            storage.StoreTenant(tenant)
            storage.StoreAuthToken(token,tenant)
            return errors.success()
        
    return errors.wrong_call_type(request.method)

# Check if current API Token + Tenant has the required READ, WRITE and PROVISION scope
@app.route("/token", methods=['GET'])
def validate_tgapi():
    if request.method == 'GET':
        # creates a temporary remote network
        HasError,resRN = rn.create_rn("TODELETE","ON_PREMISE")
        if HasError:
             return errors.token_wrong_scope("READ or READ,WRITE only")
        rn_id = resRN['data']['remoteNetworkCreate']['entity']['id']
        
        # creates a temporary Connector
        HasError,resCONN = connectors.create_connector("TODELETE",rn_id)
        if HasError:
            rn.delete_rn(rn_id)
            return errors.token_wrong_scope("READ or READ,WRITE only")
        conn_id = resCONN['data']['connectorCreate']['entity']['id']
        HasError,payload = connectors.generate_tokens(conn_id)
        if HasError:
             rn.delete_rn(rn_id)
             return errors.token_wrong_scope("READ or READ,WRITE only")
        
        rn.delete_rn(rn_id)
        return errors.success()
    return errors.wrong_call_type(request.method)

# create a "Home Network" remote network, returns the ID (and Name) of the RN created
@app.route("/homeremotenetwork", methods=['POST'])
def create_network():
    error = None
    if request.method == 'POST':
            HasError,resp = rn.create_home_rn()
            if HasError:
                return errors.rn_creation(resp)
            return resp
    else:
        return errors.wrong_call_type(request.method)

# create a Connector, generate tokens and install the Connector locally
@app.route("/connector", methods=['POST'])
def create_connector():
    if request.method == 'POST':
            content_type = request.headers.get('Content-Type')
            if (content_type == 'application/json'):
                json = request.json
                if not json['id']:
                    return errors.rn_id_missing()
                rn_id = json['id']
            
            HasError,connector_info = connectors.create_home_connector(rn_id)
            if HasError:
                return errors.connector_creation(connector_info)
            
            connector_id = connector_info['data']['connectorCreate']['entity']['id']
            HasError,payload = connectors.generate_tokens(connector_id)
            # Connector tokens are never required client side as they are stored in a staged install script
            if HasError:
                # should we delete the home remote network here?
                return errors.token_creation(payload)
            hasError,resp = connectors.install_connector()
            if hasError:
                 return errors.install_connector(resp)
            
            return errors.success()
    else:
        return errors.wrong_call_type(request.method)

@app.route("/subnet", methods=['GET'])
def get_subnet():
    if request.method == 'GET':
            subnet = network.get_subnet()
            return {"subnet":str(subnet)}
    else:
        return errors.wrong_call_type(request.method)

@app.route("/homesubnetresource", methods=['POST'])
def create_subnet_resource():
    if request.method == 'POST':
            content_type = request.headers.get('Content-Type')
            if (content_type == 'application/json'):
                json = request.json
                if not json['address']:
                    return errors.tg_res_address_error()
                address = json['address']
                if not json['remoteNetworkId']:
                    return errors.tg_res_address_error()
                rn_id = json['remoteNetworkId']

    if request.method == 'POST':
            hasError,msg = resources.create_resource_in_homenetwork(rn_id,address)
            if hasError:
                return errors.tg_res_creation_error(msg)
            else:
                 return errors.success()
    else:
        return errors.wrong_call_type(request.method)
        