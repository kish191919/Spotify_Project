import boto3
import sys
sys.path.append('./libs')
import os
import logging
import requests
import base64
import json

client_id = "***"
client_secret = "***"

# Lambda define connection at top
try:
    dynamodb = boto3.resource('dynamodb', region_name='us-west-2', endpoint_url='http://dynamodb.us-west-2.amazonaws.com')

except:
    logging.error('Could not connect to dynamodb')
    sys.exit(1)


def lambda_handler(event, context):

    headers = get_headers(client_id,client_secret)

    table = dynamodb.Table('top_tracks')

    artist_id = event['artist_id']

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
    return "SUCCESS"


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
