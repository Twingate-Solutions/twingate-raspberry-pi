import sys

sys.path.insert(1, './libs')
import tgapi

def get_show_remotenetwork_payload(token,JsonData):
    Headers = tgapi.get_api_call_headers(token)
    api_call_type = "POST"
    variables = {
        "id":JsonData['id']
    }
    Body = """
    query
        getObj($id: ID!){
            remoteNetwork(id:$id) {
                id
                name
                connectors{
                    edges{
                        node{
                            id
                            name
                        }
                    }
                }
            }
        }
    """
    return api_call_type,Headers,Body,variables

def get_delete_remotenetwork_payload(token,JsonData):
    Headers = tgapi.get_api_call_headers(token)
    api_call_type = "POST"
    variables = {
        "id":JsonData['id']
    }
    Body = """
         mutation
        createRN($id: ID!){
            remoteNetworkDelete(id:$id) {
                ok
                error
        }
    }
    """
    return api_call_type,Headers,Body,variables


def get_create_remotenetwork_payload(token,JsonData):
    Headers = tgapi.get_api_call_headers(token)
    api_call_type = "POST"
    variables = {
        "name":JsonData['name'],
        "location":JsonData['location']
    }
    Body = """
         mutation
        createRN($name: String!,$location: RemoteNetworkLocation!){
            remoteNetworkCreate(name:$name,location:$location) {
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

def get_remotenetwork_list_payload(token,JsonData):
    Headers = tgapi.get_api_call_headers(token)

    api_call_type = "POST"
    variables = { "cursor":JsonData['cursor']}

    Body = """
    query listGroup($cursor: String!)
        {
            remoteNetworks(after: $cursor, first:null) {
                pageInfo {
                endCursor
                hasNextPage
                }
                edges {
                    node {
                        id
                        name
                        updatedAt
                        createdAt
                        isActive
                        connectors{
                            edges{
                                node{
                                    id
                                    name
                                }
                            }
                        }
                    }
                }
            }
        }
    """
    return api_call_type,Headers,Body,variables

def rn_list():
    ListOfResponses = []
    hasMorePages = True
    Cursor = "0"
    while hasMorePages:
        j = tgapi.generic_api_call_handler(get_remotenetwork_list_payload,{'cursor':Cursor})
        hasMorePages,Cursor = tgapi.CheckIfMorePages(j,'remoteNetworks')
        #print("DEBUG: Has More pages:"+sthasMorePages)
        ListOfResponses.append(j['data']['remoteNetworks']['edges'])
    #output,r = StdAPIUtils.format_output(ListOfResponses,outputFormat,RemoteNetworksTransformers.GetListAsCsv)
    #print(output)
    return ListOfResponses

def simplify_rn_list(rn_raw_list):
    remote_networks = []
    if len(rn_raw_list) > 0:
        all_rns_p = rn_raw_list[0]
        if len(all_rns_p) > 0:
            for rn in all_rns_p:
                remote_networks.append({"id":rn['node']['id'],"name":rn['node']['name']})
    return remote_networks

def does_home_rn_exist():
    remote_networks = simplify_rn_list(rn_list())
    if len(remote_networks) == 0:
        return False
    else:
        for rn in remote_networks:
            rn_name = rn['name']
            if rn_name.upper() == NETWORK_NAME.upper():
                return True
        return False

def get_connectors_from_home_rn():
    home_rn_id = get_home_rn()['id']
    j = tgapi.generic_api_call_handler(get_show_remotenetwork_payload,{'id':home_rn_id})
    return j['data']['remoteNetwork']['connectors']['edges']

def get_home_rn():
    remote_networks = simplify_rn_list(rn_list())
    if len(remote_networks) == 0:
        return {}
    else:
        for rn in remote_networks:
            rn_name = rn['name']
            rn_id = rn['id']
            if rn_name.upper() == NETWORK_NAME.upper():
                return {"id":rn_id,"name":rn_name}
        return {}

def create_home_rn(REMOTE_NETWORK_NAME,NETWORK_LOCATION):
    if not does_home_rn_exist():
        err,output = create_rn(REMOTE_NETWORK_NAME,NETWORK_LOCATION)
        if not err:
            return False,output['data']['remoteNetworkCreate']['entity']
        else:
            return True,err
    else:
        return False,get_home_rn()

def create_rn(networkname,networklocation):
    j = tgapi.generic_api_call_handler(get_create_remotenetwork_payload,{'name':networkname,'location':networklocation})
    HadErrors, Msg = tgapi.check_api_error(j)
    if HadErrors:
        return True,Msg
    else:
        return False,j
def delete_rn(id):
    j = tgapi.generic_api_call_handler(get_delete_remotenetwork_payload,{'id':id})
    HadErrors, Msg = tgapi.check_api_error(j)
    if HadErrors:
        return True,Msg
    else:
        return False,j
    
def get_connectors(id):
    j = tgapi.generic_api_call_handler(get_show_remotenetwork_payload,{'id':id})
    return j



