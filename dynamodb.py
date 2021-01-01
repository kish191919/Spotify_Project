# aws에서 만든 패키지 (boto3)
# https://boto3.amazonaws.com/v1/documentation/api/latest/index.html
import boto3
import sys
import os
import logging
import requests
import base64
import json
import pickle
import pymysql
from boto3.dynamodb.conditions import Key, Attr

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


    try:
        dynamodb = boto3.resource('dynamodb', region_name='us-west-2', endpoint_url='http://dynamodb.us-west-2.amazonaws.com')
        #https://dynamodb.us-east-2.amazon.com

    except:
        logging.error('Could not connect to dynamodb')
        sys.exit(1)

    # print("success")
    # sys.exit(0)

    try:
        conn = pymysql.connect(host, user=username, passwd=password, db=database, port=port, use_unicode = True, charset='utf8')
        cursor = conn.cursor()
    except:
        logging.error("could not connect to RDS")
        sys.exit(1)

    headers = get_headers(client_id,client_secret)

    # 사용할 테이블 지정
    table = dynamodb.Table('top_tracks')
    #
    # # key를 아는 경우 (query)
    # response = table.query(
    #     # key 값을 아는 경,
    #     KeyConditionExpression=Key('artist_id').eq('00FQb4jTyendYWaN8pK0wa'),
    #
    #     # Add Filter function  gt=greater than / lt=less than
    #     FilterExpression=Attr('popularity').gt(75)
    # )

    # # Key를 모르는 경 (scan / 느림)
    # response = table.scan(
    #
    #     # Add Filter function  gt=greater than / lt=less than
    #     FilterExpression=Attr('popularity').gt(75)
    #     )

    # print(len(response['Items']))
    # sys.exit(0)
    # response = table.get_item(
    #     # Need Primary key and sort key
    #     Key={
    #         'artist_id': '00FQb4jTyendYWaN8pK0wa',
    #         'id': '0Oqc0kKFsQ6MhFOLBNZIGX'
    #     }
    # )
    # print(response)
    # sys.exit(0)

    # artist 1명 데이터
    # cursor.execute('SELECT id FROM artists LIMIT 1')

    # 전체 artist 데이터
    cursor.execute('SELECT id FROM artists')


    for (artist_id, ) in cursor.fetchall():
        URL = "https://api.spotify.com/v1/artists/{}/top-tracks".format(artist_id)
        params = {
            'country' : 'US'
        }
        r = requests.get(URL, params = params, headers = headers)

        raw = json.loads(r.text)



        for track in raw['tracks']:
            # Add artist_id
            data = {
                'artist_id': artist_id
            }

            data.update(track)

            table.put_item(
            Item = data
            )

    print(table)
    sys.exit(0)





def get_headers(client_id, client_secret):

    endpoint = "https://accounts.spotify.com/api/token"
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
