import os
import random
import uuid
import logging
from os.path import exists

DATAFILEPATH = "./store/"
TOKENFILE = os.path.join(DATAFILEPATH, ".token_")
URLFILE = os.path.join(DATAFILEPATH, ".tenant_")

def is_token_valid(atoken):
    if len(atoken) == 134:
        return True
    else:
        return False

def CheckAndCreateDataFolderIfNeeded():
    if not os.path.exists(DATAFILEPATH):
        logging.debug("Creating Folder to Store Token and Tenant Name.")
        os.makedirs(DATAFILEPATH)
        logging.debug("Created:"+str(DATAFILEPATH))

def deleteAFile(filename):
    CheckAndCreateDataFolderIfNeeded()
    try:
        os.remove(filename)
    except:
        pass

def DeleteSessionFiles():
    CheckAndCreateDataFolderIfNeeded()
    deleteAFile(URLFILE)
    deleteAFile(TOKENFILE)

def StoreTenant(tenant):
    CheckAndCreateDataFolderIfNeeded()
    SessionFileName = URLFILE
    deleteAFile(SessionFileName)
    text_file = open(SessionFileName, "w+")
    text_file.write(tenant)
    text_file.close()

def StoreAuthToken(token,tenant):
    CheckAndCreateDataFolderIfNeeded()
    SessionFileName = TOKENFILE
    deleteAFile(SessionFileName)
    text_file = open(SessionFileName, "wb+")
    #encodedtoken = encode(token,tenant).decode('utf-8')
    text_file.write(encode(token,tenant))

    text_file.close()

def GetUrl():
    SessionFileName = URLFILE
    logging.debug("Getting URL From Session File: "+str(SessionFileName))
    try:
        text_file = open(SessionFileName, "r")
        tenant = text_file.read()
        logging.debug("Tenant Name: "+str(tenant))
        fullprodurl = "https://"+tenant+".twingate.com/api/graphql/"
        fullurl=fullprodurl
        logging.debug("Full Url: "+str(fullurl))
        text_file.close()
        return fullurl,tenant
    except:
        print("Cannot get Tenant: Session does not exist.")
        exit(1)


def GetAuthToken(tenant):
    SessionFileName = TOKENFILE
    logging.debug("Getting Token From Session File: "+str(SessionFileName))
    try:
        text_file = open(SessionFileName, "rb")
        token = text_file.read()
        logging.debug("Encrypted Token: "+str(token))
        detoken = decode(token,tenant)
        logging.debug("Decrypted Token: "+str(detoken))
        text_file.close()
        return detoken
    except:
        print("Cannot get Token: Session does not exist.")
        exit(1)

def encode(cleartext,key):
    StubStr = uuid.uuid4().hex
    StringToEnc = StubStr+cleartext
    reps = (len(StringToEnc)-1)//len(key) +1
    a1 = StringToEnc.encode('utf-8')
    key = (key * reps)[:len(StringToEnc)].encode('utf-8')
    cipher = bytes([i1^i2 for (i1,i2) in zip(a1,key)])
    return cipher

def decode(cipher,key):
    reps = (len(cipher)-1)//len(key) +1
    key = (key * reps)[:len(cipher)].encode('utf-8')
    clear = bytes([i1^i2 for (i1,i2) in zip(cipher,key)])
    clearStr = clear.decode('utf-8')[32:]
    return clearStr

