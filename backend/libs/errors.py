import logging

def wrong_token_format():
    return {"errors":[{"message":"Wrong token format"}]};

def wrong_call_type():
    return {"errors":[{"message":"Wrong call type"}]};

def token_or_tenant_missing(what_is_missing):
    return {"errors":[{"message":what_is_missing+" is missing."}]};

def rn_id_missing():
    return {"errors":[{"message":"ID of Remote Network is missing."}]};

def token_wrong_scope(current_scope):
    return {"errors":[{"message":"API token requires Read, Write and Provision permissions. Your current API Token seems to be "+str(current_scope)}]};

def rn_creation():
    return {"errors":[{"message":"cannot create home remote network."}]};

def connector_creation(message):
    return {"errors":[{"message":"cannot create connector in home remote network: "+message}]};

def connector_list():
    return {"errors":[{"message":"cannot list connectors in home remote network."}]};

def connector_exists():
    return {"errors":[{"message":"connector for home network already exists."}]};

def token_creation():
    return {"errors":[{"message":"cannot create tokens for connector in home remote network."}]};

def tg_api_error():
    return {"errors":[{"message":"Twingate API error."}]};

def tg_res_address_error():
    return {"errors":[{"message":"address missing."}]};

def tg_res_creation_error(msg):
    return {"errors":[{"message":"could not create Resource: "+msg}]};

def connector_install_error(rcode):
    return {"errors":[{"message":"Error installing Connector.","return_code":str(rcode)}]};

def connector_uninstall_error(rcode):
    return {"errors":[{"message":"Error installing Connector.","return_code":str(rcode)}]};


def process_tg_api_response(response):
    if(response.status_code >= 300):
        if(response.status_code == 500):
            logging.debug("API Error: {} - Hint: {} - Message: {}".format(response.status_code, "Try logging back in.",response.text))
            print("API Error: {} - Hint: {} - Message: {}".format(response.status_code, "Try logging back in.",response.text))
            #print("API Error Code: "+str(response.status_code))
            return False
        else:
            logging.debug("API Error: {} - Message: {}".format(response.status_code,response.text))
            print("API Error: {} - Message: {}".format(response.status_code,response.text))
            #print("API Error Code: "+str(response.status_code))
            return False
    else:
        RespContent = str(response.text)
        if(RespContent.startswith("<!doctype html>")):
            logging.debug("API Error: {} - Message: {}".format(response.status_code,"Response received is in HTML Format"))
            print("API Error: {} - Message: {}".format(response.status_code,"Response received is in HTML Format"))
            return False
        else:
            return True
