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

    cursor.execute("SELECT * FROM artists")
    colnames = [d[0] for d in cursor.description]
    artists = [dict(zip(colnames, raw)) for raw in cursor.fetchall()]
    artists = pd.DataFrame(artists)

    artists.to_parquet('artists.parquet', engine='pyarrow', compression='snappy')

    dt = datetime.utcnow().strftime("%Y-%m-%d")

    s3 = boto3.resource('s3',region_name='us-east-2')
    object = s3.Object('spotify-artist-project', 'artists/dt={}/artists.parquet'.format(dt))
    data = open('artists.parquet', 'rb')
    object.put(Body=data)


if __name__=='__main__':
    main()
