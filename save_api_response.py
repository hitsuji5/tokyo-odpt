import requests
import sys
import json
from config import API_URL, ACCESS_TOKEN

if __name__ == '__main__':
    rdf_type = sys.argv[1]
    filename = sys.argv[2]
    payload = {'acl:consumerKey': ACCESS_TOKEN,
               "odpt:operator": "odpt.Operator:Toei"}
    r = requests.get(API_URL + rdf_type, params=payload)
    data = r.json()
    print len(data)
    json.dump(data, open(filename, "wb"))
