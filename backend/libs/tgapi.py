import requests
import json
import logging
import sys

sys.path.insert(1, './libs')
import storage
import errors

def get_api_call_headers(token):
    DefaultHeaders = {
        'X-API-KEY': token
    }

    return DefaultHeaders

def CheckIfMorePages(jsonResults,objName):
    pInfo = jsonResults['data'][objName]['pageInfo']
    hasNextPage = pInfo['hasNextPage']
    if hasNextPage:
        Cursor = pInfo['endCursor']
        return True,Cursor
    else:
        return False,None

# Generic API Handler with embedded processing of Output
def generic_api_call_handler(get_res_func,res_data):
        FULLURL,TENANT = storage.GetUrl()
        TOKEN = storage.GetAuthToken(TENANT)
        CallType,Headers,Body,variables = get_res_func(TOKEN,res_data)

        logging.debug("method:"+str(CallType))
        logging.debug("URL:"+str(FULLURL))
        logging.debug("Data:"+str(Body))
        logging.debug("headers:"+str(Headers))
        logging.debug("variables:" + str(variables))

        if variables:
            response = requests.request(method=CallType, url=FULLURL, json={'query': Body, 'variables':variables}, headers=Headers)
        else:
            response = requests.request(method=CallType, url=FULLURL, json={'query': Body}, headers=Headers)
        
        logging.debug("Response:" + str(response.text))
        isAPICallOK = errors.process_tg_api_response(response)

        if(not isAPICallOK):
            return errors.tg_api_error()
        else:
            logging.debug("Converting Response to JSON Object.")
            json_object = json.loads(response.text)
            return json_object
        
def check_api_error(payload):
    if 'errors' in payload.keys():
        return True, payload['errors'][0]['message']
    else:
        return False, None