import sys
import numpy as np
import pandas as pd
import requests
import base64
import json
import logging

client_id = "ac43daedc6184dc29feb74a63bea4427"
client_secret = "adb5c0e040604da59c1c9e140749ea8c"


def main():
    endpoint = "https://accounts.spotify.com/api/token"

    # python3 add .encode('utf-8')).decode('ascii')
    encoded = base64.b64encode("{}:{}".format(client_id, client_secret).encode('utf-8')).decode('ascii')

    headers = {
        "Authorization": "Basic {}".format(encoded)
    }

    payload = {
        "grant_type" : "client_credentials"
    }

    r = requests.post(endpoint, data=payload, headers=headers)

    access_token = json.loads(r.text)['access_token']

    headers ={
        
    }


    print('fastcampus')




if __name__=='__main__':
    main()
