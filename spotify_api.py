import sys
import numpy as np
import pandas as pd
import requests
import base64
import json
import logging
import pickle
import pymysql


# make pickle file
# pickle.dump(' ', open("./client_id.plk","wb"))
# client_id = "1"
client_id = pickle.load(open('./client_id.plk','rb'))
client_secret = pickle.load(open('./client_secret.plk','rb'))

host = pickle.load(open('./host.plk','rb'))
port = 3306
username = "danny"
database = "production"
password = pickle.load(open('./password.plk', 'rb'))



def main():

    # try:
    #     # use_unicode if some data was not written in English, such as korean
    #     conn = pymysql.connect(host, user=username, passwd=password, db=database, port=port, use_unicode = True, charset='utf8')
    #     # cursor 를 통해서 query를 할 수 있음
    #     cursor = conn.cursor()
    # except:
    #     logging.error("could not connect to RDS")
    #     sys.exit(1)
    #
    # cursor.execute("SHOW TABLES")
    # # 하나만 갖고올때는 fetchone 을 사용. 그러나 많이 쓰이지는 않음
    # print(cursor.fetchall())


    # artist_id =
    # genre =
    # query = "INSERT INTO artist_genres (artist_id, genre) VALUES ('2345', 'rock')"
    # query = "INSERT INTO artist_genres (artist_id, genre) VALUES ('%s', '%s')" % (artist_id, genre)

    # query = "INSERT INTO artist_genres (artist_id, genre) VALUES ('{}', '{}')".format('12345', 'hip-hop')
    # cursor.execute(query)
    # conn.commit()



    # print("success")
    # sys.exit(0)



    headers = get_headers(client_id,client_secret)
    # print(headers)

    # Spotify Search api
    params = {
        "q":"BTS",
        "type":"artist",
        "limit": "2"  # limit the information
        }

    # r = requests.get("https://api.spotify.com/v1/search", params=params, headers=headers)
    # print(r.status_code)
    # print(r.text)
    # print(r.headers)
    # sys.exit(0)

    r = requests.get("https://api.spotify.com/v1/search", params=params, headers=headers)
    # print(r.text)
    # sys.exit(0)

    raw = json.loads(r.text)
    # print(raw['artists'])
    # print(raw.keys())
    print(raw['artists'].keys())
    sys.exit(0)



    # try:
    #     r = requests.get("https://api.spotify.com/v1/search", params=params, headers=headers)
    #
    # except:
    #     logging.error(r.text)
    #     sys.exit(1)
    #     # sys.exit(0)

    r = requests.get("https://api.spotify.com/v1/search", params=params, headers=headers)
    if r.status_code != 200:
        logging.error(json.loads(r.text))
        # logging.error(r.text)


        if r.status_code == 429:

            retry_after = json.loads(r.headers)['Retry-After']
            time.sleep(int(retry_after))

            r = requests.get("https://api.spotify.com/v1/search", params=params, headers=headers)

        # access_token expired
        elif r.status_code == 401:

            headers = get_headers(client_id, client_secret)
            r = requests.get("https://api.spotify.com/v1/search", params=params, headers=headers)

        else:
            sys.exit(1)

    # print(r.text)
    # print(type(r.text))
    # sys.exit(0)

    # Get BTS' Albums

    r = requests.get("https://api.spotify.com/v1/artists/3Nrfpe0tUJi4K4DXYWgMUX/albums", headers=headers)

    raw = json.loads(r.text)
    # print(raw)
    # sys.exit(0)

    total = raw['total']
    offset = raw['offset']
    limit = raw['limit']
    next = raw['next']

    albums = []
    albums.extend(raw['items'])

    # if you want 100 count, while count < 100 and next:
    while next:

        r = requests.get(raw['next'], headers=headers)
        raw = json.loads(r.text)
        next = raw['next']
        print(next)

        albums.extend(raw['items'])

    print(len(albums))


def get_headers(client_id, client_secret):
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

    # Check the status of access token
    # print(r.status_code)
    # print(r.headers)
    # print(r.text)
    # print(type(r.text))
    # sys.exit(0)

    # text is <class 'str'> so we need to convert it as dictionary type
    # output :  <class 'dict'>
    # access_token = json.loads(r.text)
    # print(type(access_token))
    # print(access_token)
    # sys.exit(0)

    access_token = json.loads(r.text)['access_token']

    headers = {
        "Authorization": "Bearer {}".format(access_token)
        }

    return headers



if __name__=='__main__':
    main()
