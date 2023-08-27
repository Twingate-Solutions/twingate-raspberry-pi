import sys
import io

sys.path.insert(1, './libs')
sys.path.insert(1, '../resources')
import tgapi
import storage
import errors
import groups

HOME_SUBNET_RES_NAME = "Home Subnet"
def get_home_network_resource_payload(token,JsonData):
    Headers = tgapi.get_api_call_headers(token)

    api_call_type = "POST"
    variables = {"fname":HOME_SUBNET_RES_NAME}

    Body = """
    query getResources($fname: String!)
        {
            resources(filter:{name:{eq:$fname}}) {
                edges {
                    node {
                        id
                        name
                        createdAt
                        updatedAt
                        isActive
                    }
                }   
            }
        }
    """
    return api_call_type,Headers,Body,variables

def get_create_resource_payload(token,JsonData):
    Headers = tgapi.get_api_call_headers(token)
    api_call_type = "POST"
    variables = {"address":JsonData['address'] ,"name":JsonData['name'],"remoteNetworkId":JsonData['remoteNetworkId'],"groupIds":JsonData['groupIds']}
    Body = """
        mutation
            ObjCreate($address: String!,$name:String!,$remoteNetworkId:ID!,$groupIds:[ID!]){
            resourceCreate(address: $address, groupIds: $groupIds, name: $name, remoteNetworkId: $remoteNetworkId) {
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

def create_resource_in_homenetwork(rn_id,address):
    haserror,res = get_home_network_resource()
    #print(res)
    existing_resources = res['data']['resources']['edges']
    if len(existing_resources) == 0:
        print(res)
        name = "Home Subnet"
        hasError,group_id = groups.get_everyone_groupid()
        return create_resource(rn_id,address,name,group_id)
    else:
        return True,"Resource already exists"
    
def create_resource(rn_id,address,name,group_id):
    j = tgapi.generic_api_call_handler(get_create_resource_payload,{'address':address,'name':name,'remoteNetworkId':rn_id,'groupIds':[group_id]})
    HadErrors, Msg = tgapi.check_api_error(j)
    if HadErrors:
        return True,Msg
    else:
        return False,j
    

def get_home_network_resource():
    Cursor = "0"
    j = tgapi.generic_api_call_handler(get_home_network_resource_payload,{})
    HadErrors, Msg = tgapi.check_api_error(j)
    #print(j)
    if HadErrors:
        return True,Msg
    else:
        return False,j 
    