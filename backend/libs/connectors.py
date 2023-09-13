import sys,os,re
import io
import shutil
import subprocess
from subprocess import check_output

sys.path.insert(1, './libs')
sys.path.insert(1, '../resources')
import tgapi
import storage
import errors

dirname = os.path.dirname(__file__)
INSTALL_STUB = os.path.join(dirname, '../resources/stub_install_script.sh')
INSTALL_INSTANCE = os.path.join(dirname, '../resources/install_connector.sh')

def get_generate_tokens_payload(token,JsonData):
    Headers = tgapi.get_api_call_headers(token)

    api_call_type = "POST"
    variables = {"id":JsonData['id']}

    Body = """
       mutation GenerateTokens($id: ID!){
        connectorGenerateTokens(connectorId: $id) {
            ok
            error
            connectorTokens{
                accessToken
                refreshToken
            }
        }
    }
    """
    return api_call_type,Headers,Body,variables

def get_connector_list_payload(token,JsonData):
    Headers = tgapi.get_api_call_headers(token)

    api_call_type = "POST"
    variables = {"id":JsonData['id']}

    Body = """
    query getConnectors($id: ID!)
        {
            remoteNetwork(id: $id) {
                        id
                        name
                        isActive
                        connectors{
                            edges{
                                node{
                                    id
                                    name
                                    state
                                }
                            }
                        }
                    
                
            }
        }
    """
    return api_call_type,Headers,Body,variables

def get_create_connector_payload(token,JsonData):
    Headers = tgapi.get_api_call_headers(token)
    api_call_type = "POST"
    variables = {
        "connName":JsonData['name'],
        "remoteNetworkID":JsonData['id']
    }
    Body = """
    mutation PM_CreateConnector($connName: String!, $remoteNetworkID: ID!){
        connectorCreate(name: $connName,remoteNetworkId: $remoteNetworkID) {
            ok
            error
            entity{
                id
                name
            }
        }
    }
    """
    return api_call_type,Headers,Body,variables

def get_delete_connector_payload(token,JsonData):
    Headers = tgapi.get_api_call_headers(token)
    api_call_type = "POST"
    variables = {
        "id":JsonData['id']
    }
    Body = """
    mutation DeleteConnector($id: ID!){
        connectorDelete(id: $id) {
            ok
            error
        }
    }
    """
    return api_call_type,Headers,Body,variables

def get_connector_list(id):
    j = tgapi.generic_api_call_handler(get_connector_list_payload,{'id':id})
    HadErrors, Msg = tgapi.check_api_error(j)
    if HadErrors:
        return True,Msg
    else:
        return False,j

def delete_connector(id):
    j = tgapi.generic_api_call_handler(get_delete_connector_payload,{'id':id})
    HadErrors, Msg = tgapi.check_api_error(j)
    if HadErrors:
        return True,Msg
    else:
        return False,j
       
def create_connector(name,id):
    j = tgapi.generic_api_call_handler(get_create_connector_payload,{'name':name,'id':id})
    HadErrors, Msg = tgapi.check_api_error(j)
    if HadErrors:
        return True,Msg
    else:
        return False,j

def get_new_connector_name(CONNECTOR_NAME_STUB,payload):
    validConnectorNames = []
    regstring = CONNECTOR_NAME_STUB+" ([\d]+)"
    #pattern = re.compile(regstring)

    connNumbers = [0]  
    connectors = payload['data']['remoteNetwork']['connectors']['edges']
    for conn in connectors:
        connName = conn['node']['name']
        if re.match(regstring,connName, re.IGNORECASE):
            result = re.match(regstring,connName, re.IGNORECASE)
            if result.groups():
                connNumber = int(result.groups(1)[0])
                connNumbers.append(connNumber)
            
            validConnectorNames.append(connName)

    newNum = max(connNumbers) + 1
    newName = CONNECTOR_NAME_STUB+" "+str(newNum)
    return newName

def check_for_running_connector():
    status = os.system('systemctl is-active --quiet twingate-connector')
    print(status)
    if status == 0:
        return True
    else:
        return False

def create_home_connector(CONNECTOR_NAME_STUB,id):
    if check_for_running_connector():
        return True,"Connector already installed on host"
    else:
        HasError,all_connectors = get_connector_list(id)
        if HasError:
            return True,all_connectors
        else:
            NewConnName = get_new_connector_name(CONNECTOR_NAME_STUB,all_connectors)
            #print(NewConnName)
            return create_connector(NewConnName,id)

def generate_tokens(id):
    j = tgapi.generic_api_call_handler(get_generate_tokens_payload,{'id':id})
    HadErrors, Msg = tgapi.check_api_error(j)
    if HadErrors:
        return True,Msg
    else:
        accessToken = j['data']['connectorGenerateTokens']['connectorTokens']['accessToken']
        refreshToken = j['data']['connectorGenerateTokens']['connectorTokens']['refreshToken']
        url,tenant = storage.GetUrl()
        provision_install_script(accessToken,refreshToken,tenant)
    return False,j

def provision_install_script(accessToken,refreshToken,tenant):
    shutil.copyfile(INSTALL_STUB, INSTALL_INSTANCE)
    # Read in the file
    with open(INSTALL_STUB, 'r') as file :
        filedata = file.read()

    # Replace the target string
    filedata = filedata.replace('<ACCESSTOKEN>', accessToken).replace('<REFRESHTOKEN>',refreshToken).replace('<TENANT>',tenant)

    # Write the file out again
    with open(INSTALL_INSTANCE, 'w') as file:
        file.write(filedata)
    return True

def uninstall_connector():
    try:
        output = check_output(["sudo","apt","remove","twingate-connector"], text=True)
        #print(output)
        return {"status":"OK"}
    except subprocess.CalledProcessError as e:
        return errors.connector_uninstall_error(e.returncode)
    
def run_install_script(filepath):
    try:
        output = check_output(["sudo","sh",filepath], text=True)
        #print(output)
        return False,output
    except subprocess.CalledProcessError as e:
        return True,errors.connector_install_error(e.returncode)

def delete_install_script(filepath):
    return True

def install_connector():
    hasError,res = run_install_script(INSTALL_INSTANCE)
    return hasError,res
