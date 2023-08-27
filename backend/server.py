# requires flask
# requires nmap (system) and python-namp

# pip install python-nmap (as sudo for OS fingerprinting)

# run with flask --app server run -h 127.0.0.1 -p 10064

from flask import Flask
from flask import request
import sys

sys.path.insert(1, './libs')
import storage
import errors
import network
import connectors
import rn

app = Flask(__name__)

# needed functions
## store API token - DONE
## store tenant name - DONE
## create Remote Network - DONE
## create connector - DONE 
## install connector - DONE
## check connector status
## detect subnet - DONE
## create resources

# stores tenant name and API token locally
@app.route("/store/tenant", methods=['POST'])
def store_tenant():
    error = None
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
            return ""
    return errors.wrong_call_type()

# Check if current API Token + Tenant has the required READ, WRITE and PROVISION scope
@app.route("/tgapi/validate", methods=['GET'])
def validate_tgapi():
    error = None
    if request.method == 'GET':
        HasError,resRN = rn.create_rn("TODELETE","ON_PREMISE")
        if HasError:
             return errors.token_wrong_scope("READ only")

        rn_id = resRN['data']['remoteNetworkCreate']['entity']['id']
    
        HasError,resCONN = connectors.create_connector("TODELETE",rn_id)
        if HasError:
            rn.delete_rn(rn_id)
            return errors.token_wrong_scope("READ only")
        conn_id = resCONN['data']['connectorCreate']['entity']['id']
        HasError,payload = connectors.generate_tokens(conn_id)
        if HasError:
             rn.delete_rn(rn_id)
             return errors.token_wrong_scope("READ, WRITE only")
        
        rn.delete_rn(rn_id)
        return {"status":"APIScopeOK"}
    return errors.wrong_call_type()

# create a Home Network remote network, returns the ID and Name of the RN created
@app.route("/creatern", methods=['GET'])
def get_networks():
    error = None
    if request.method == 'GET':
            HasError,resp = rn.create_home_rn()
            if HasError:
                return errors.rn_creation()
            return resp
    else:
        return errors.wrong_call_type()
    
@app.route("/connectors", methods=['GET'])
def get_connectors():
    error = None
    if request.method == 'GET':
            resp = rn.get_connectors_from_home_rn()
            
            return resp
    else:
        return errors.wrong_call_type()

@app.route("/createconnector", methods=['POST'])
def create_connector():
    error = None
    if request.method == 'POST':
            content_type = request.headers.get('Content-Type')
            if (content_type == 'application/json'):
                json = request.json
                if not json['id']:
                    return errors.rn_id_missing()
                rn_id = json['id']
            #home_rn = rn.create_home_rn()
            #connector_info = connectors.create_home_connector(home_rn['id'])
            HasError,connector_info = connectors.create_home_connector(rn_id)
            if HasError:
                # should we delete the home remote network here?
                return errors.connector_creation(connector_info)
            
            connector_id = connector_info['data']['connectorCreate']['entity']['id']
            HasError,token_payload = connectors.generate_tokens(connector_id)
            if HasError:
                # should we delete the home remote network here?
                return errors.token_creation()
            resp = connectors.install_connector()
            return resp
    else:
        return errors.wrong_call_type()
    
@app.route("/subnet", methods=['GET'])
def get_subnet():
    error = None
    if request.method == 'GET':
            subnet = network.get_subnet()
            
            return {"subnet":str(subnet)}
    else:
        return errors.wrong_call_type()
    