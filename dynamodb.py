# aws에서 만든 패키지 (boto3)
# https://boto3.amazonaws.com/v1/documentation/api/latest/index.html
import boto3
import sys
import os
import logging


def main():

    try:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-2', endpoint_url='http://dynamodb.us-east-2.amazon.com')

    except:
        logging.error('Could not connect to dynamodb')
        sys.exit(1)

    print('Success')





if __name__=='__main__':

    main()
