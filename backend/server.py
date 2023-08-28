# requires flask
# requires nmap (system) and python-namp

# pip install python-nmap (as sudo for OS fingerprinting)
# run with sudo flask --app server run -h 127.0.0.1 -p 10064 (sudo required because installing a Connector requires it)

from flask import Flask
from flask import request
import sys

# internal library imports
sys.path.insert(1, './libs')
import storage
import errors
import network
import connectors
import resources
import rn

app = Flask(__name__)

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
                 return errors.intall_connector(resp)
            
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
        