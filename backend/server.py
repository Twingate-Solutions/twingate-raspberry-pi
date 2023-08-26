# requires flask

# run with flask --app server run -h 127.0.0.1 -p 10064

from flask import Flask
from flask import request
import sys

sys.path.insert(1, './libs')
import storage
import errors

app = Flask(__name__)

# needed functions
## store API token (check if it's read / write, permission)
## store tenant name
## create Remote Network
## create connector
## install connector
## check connector status
## detect subnet
## create resources

#
@app.route("/store/token", methods=['POST'])
def store_api_token():
    error = None
    if request.method == 'POST':
        content_type = request.headers.get('Content-Type')
        if (content_type == 'application/json'):
            json = request.json
        if json['token']:
            token = json['token']
            if not storage.is_token_valid(token):
                return errors.wrong_token_format()
            else:
                storage.store_token(token)
                return ""
    return errors.wrong_call_type()