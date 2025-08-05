import json
from app import app
import awsgi

def lambda_handler(event, context):
    return awsgi.response(app, event, context)