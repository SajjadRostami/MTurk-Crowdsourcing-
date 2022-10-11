import json
import boto3
import xmltodict as xmltodict
import mysql.connector
import time

mturk = boto3.client('mturk',
                     region_name='us-east-1',
                     aws_access_key_id='',
                     aws_secret_access_key='/FS',
                     endpoint_url='https://-requester.us-east-1.amazonaws.com'
                     )
# You will need the following library
# to help parse the XML answers supplied from MTurk
# Install it in your local environment with
# pip install xmltodict
import xmltodict

# Use the hit_id previously created
hit_id = '32FESTC2OKG7XCOVEDMUZUQV41GUCT'
# We are only publishing this task to one Worker
# So we will get back an array with one item if it has been completed
worker_results = mturk.list_assignments_for_hit(HITId=hit_id, AssignmentStatuses=['Submitted'])
print (worker_results)
