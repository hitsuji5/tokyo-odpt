import requests
import time
from datetime import datetime
import csv
from google.cloud import storage
# from oauth2client.client import GoogleCredentials
# credentials = GoogleCredentials.get_application_default()
# from googleapiclient import discovery
# storage = discovery.build('storage', 'v1', credentials=credentials)

bus_res_keys = [
    u'dc:date', u'dct:valid', u'odpt:busroute', u'odpt:busroutePattern', u'odpt:busNumber', u'odpt:operator',
    u'odpt:startingBusstopPole', u'odpt:terminalBusstopPole', u'odpt:fromBusstopPole', u'odpt:toBusstopPole',
    u'odpt:fromBusstopPoleTime', u'geo:lat', u'geo:long', u'odpt:azimuth', u'odpt:doorStatus', u'odpt:progress', u'odpt:speed'
]
PROJECT_ID = 'tokyo-odpt'
BUCKET = 'odpt-data'
ACCESS_TOKEN = ''
API_URL = 'https://api-tokyochallenge.odpt.org/api/v4/'
NUM_REQUEST = 240
FREQUENCY = 13

def upload_file(file, filename, retry_num=5):
    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(BUCKET)
    blob = bucket.blob(filename)
    for _ in range(retry_num):
        try:
            blob.upload_from_file(file)
            return True
        except:
            print("Fail to upload {}".format(output_file))
            continue
    return False


class ODPTClient(object):
    def __init__(self):
        self.rdf_type_bus = 'odpt:Bus'

    def get_bus_state(self, retry_num=5):
        payload = {'acl:consumerKey': ACCESS_TOKEN}
        for _ in range(retry_num):
            try:
                r = requests.get(API_URL + self.rdf_type_bus, params=payload)
                return r.json()
            except:
                print("Fail to connect Bus API")
                continue
        return None



if __name__ == '__main__':
    odpt_client = ODPTClient()
    while True:
        output_file = 'bus_{}.csv'.format(datetime.now().strftime("%Y%m%d%H%M%S"))
        f = open(output_file, 'a')
        writer = csv.writer(f, lineterminator='\n')

        print("writing to {}".format(output_file))
        for i in range(NUM_REQUEST):
            data = odpt_client.get_bus_state()
            if data is None:
                time.sleep(3)
                continue

            print(len(data))
            if i == 0:
                writer.writerow(bus_res_keys)
            writer.writerows([[record.get(key, None) for key in bus_res_keys] for record in data])
            time.sleep(FREQUENCY)

        f.close()
        upload_file(open(output_file, 'rb'), output_file)



