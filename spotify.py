import sys
import os
import logging
import boto3
import requests
import base64
import pymysql
from datetime import datetime
import pickle
import json
import pandas as pd
import jsonpath

client_id = pickle.load(open('./client_id.plk','rb'))
client_secret = pickle.load(open('./client_secret.plk','rb'))

host = pickle.load(open('./host.plk','rb'))
port = 3306
username = "danny"
database = "production"
password = pickle.load(open('./password.plk', 'rb'))



def main():

    # RDS - Aritst_ID 갖고오고
    # Spotyfy API를 통해서 데이터를 불러오고
    # .json 파일로 갖고와서
    # S3에 입력

    try:
        # use_unicode if some data was not written in English, such as korean
        conn = pymysql.connect(host, user=username, passwd=password, db=database, port=port, use_unicode = True, charset='utf8')
        # cursor 를 통해서 query를 할 수 있음
        cursor = conn.cursor()
    except:
        logging.error("could not connect to RDS")
        sys.exit(1)

    headers = get_headers(client_id,client_secret)

    cursor.execute("SELECT id FROM artists")

    top_track_keys = {
        "id": "id",
        "name":"name",
        "popularity":"popularity",
        "external_url":"external_urls.spotify"
    }

    # Top tracks Spotify 가져오고
    top_tracks =[]
    for (id, ) in cursor.fetchall():
        URL = "https://api.spotify.com/v1/artists/{}/top-tracks".format(id)
        params = {
            'country' : 'US'
        }
        r = requests.get(URL, params = params, headers = headers)
        raw = json.loads(r.text)

        for i in raw['tracks']:
            top_track = {}
            for k, v in top_track_keys.items():
                # i data 중에 v path를 이용하여 value값을 입력
                top_track.update({k: jsonpath.jsonpath(i, v)})
                top_track.update({'artist_id': id})
                top_tracks.append(top_track)


    # # Top tracks Spotify 가져오고  / parquet 파일일 경우
    # top_tracks =[]
    # for (id, ) in cursor.fetchall():
    #     URL = "https://api.spotify.com/v1/artists/{}/top-tracks".format(id)
    #     params = {
    #         'country' : 'US'
    #     }
    #     r = requests.get(URL, params = params, headers = headers)
    #     raw = json.loads(r.text)
    #     top_tracks.extend(raw['tracks'])

    # List of dictionaries 로 변환
    track_ids = [i['id'][0] for i in top_tracks]

    top_tracks = pd.DataFrame(top_tracks)
    top_tracks.to_parquet('top_tracks.parquet', engine='pyarrow', compression='snappy')

    dt = datetime.utcnow().strftime("%Y-%m-%d")

    # Parquet일 경우
    s3 = boto3.resource('s3')
    object = s3.Object('spotify-artist-project', 'top-tracks/dt={}/top_tracks.parquet'.format(dt))
    data = open('top_tracks.parquet', 'rb')
    object.put(Body=data)

    # print("sucess")
    # sys.exit(0)
    # track_ids


    #
    # # os.linesep 이란 '\n' 개행문자를 공급
    # with open('top_tracks.json', 'w') as f:
    #     for i in top_tracks:
    #         json.dump(i, f)
    #         f.write(os.linesep)

    # Parquet 이 아닐경
    # s3m= boto3.resource('s3')
    # object = s3.Object('spotify-artist-project', 'dt={}/top_tracks.json'.format(dt))
    # data = open('top_tracks.json', 'rb')
    # object.put(Body=data)

    # S3 import
    tracks_batch = [track_ids[i: i+100] for i in range(0, len(track_ids), 100)]

    audio_features = []
    for i in tracks_batch:
        ids = ','.join(i)
        URL = "https://api.spotify.com/v1/audio-features/?ids={}".format(ids)

        r = requests.get(URL, headers=headers)
        raw = json.loads(r.text)

        audio_features.extend(raw['audio_features'])

    audio_features = pd.DataFrame(audio_features)
    audio_features.to_parquet('audio-features.parquet', engine = 'pyarrow', compression='snappy')

    s3 = boto3.resource('s3')
    object = s3.Object('spotify-artist-project', 'audio-features/dt={}/top_tracks.parquet'.format(dt))
    data = open('audio-features.parquet', 'rb')
    object.put(Body=data)

    print("success All")


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

    access_token = json.loads(r.text)['access_token']

    headers = {
        "Authorization": "Bearer {}".format(access_token)
        }

    return headers

if __name__=='__main__':
    main()
