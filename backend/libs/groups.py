import sys,os,re
import io
sys.path.insert(1, './libs')
sys.path.insert(1, '../resources')
import tgapi
import storage
import errors

def get_everyone_group_payload(token,JsonData):
    Headers = tgapi.get_api_call_headers(token)

    variables = { "cursor":JsonData['cursor']}

    api_call_type = "POST"

    Body = """
    query listGroup($cursor: String!)
            {
  groups(after: $cursor, first:null, filter:{name:{eq:"Everyone"}}) {
    pageInfo {
      endCursor
      hasNextPage
    }
    edges {
      node {
        id
        name
        createdAt
        updatedAt
        isActive
        type
        resources {
            edges{
                node{
                    id
                    name
                    address {
                        type
                        value
                    }
                    isActive
                }
            }
        }
      }
    }
  }
}

    """

    return api_call_type,Headers,Body,variables

def get_everyone_groupid():
    Cursor = "0"
    j = tgapi.generic_api_call_handler(get_everyone_group_payload,{'cursor':Cursor})
    HadErrors, Msg = tgapi.check_api_error(j)
    if HadErrors:
        return True,Msg
    else:
        groupid = j['data']['groups']['edges'][0]['node']['id']
        return False,groupid 
    

