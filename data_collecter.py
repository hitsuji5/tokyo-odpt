import requests
import time
from datetime import datetime
import csv
import os
from google.cloud import storage
from config import PROJECT_ID, BUCKET, ACCESS_TOKEN, API_URL, bus_res_keys
NUM_REQUEST = 240
FREQUENCY = 13

def upload_file(file, filename, retry_num=5):
    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(BUCKET)
    blob = bucket.blob(filename)
    for _ in range(retry_num):
        try:
            blob.upload_from_file(file)
            print("Succeed to upload {}".format(output_file))
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
                data = r.json()
                print("Collect {} bus data".format(len(data)))
                return data
            except:
                time.sleep(0.5)
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
                print("Fail to connect Bus API...")
                time.sleep(3)
                print("Retry")
                continue

            if i == 0:
                writer.writerow(bus_res_keys)
            writer.writerows([[record.get(key, None) for key in bus_res_keys] for record in data])
            time.sleep(FREQUENCY)

        f.close()
        upload_file(open(output_file, 'rb'), output_file)
        os.remove(output_file)


