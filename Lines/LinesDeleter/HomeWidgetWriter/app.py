import json
from _decimal import Decimal
from http.client import responses

import boto3

from models import HomeWidget
from utils import getDBConnection, getUserId
from utils.dynamoDBUtils import DecimalEncoder
from values import configs


def lambda_handler(event, context):
    # Use the DynamoDB client instead of the table resource for batch_get_item
    dynamoDb = getDBConnection()
    homeWidgetsDb = dynamoDb.Table(configs.HOME_WIDGETS_TABLE_NAME)
    # Read the payload from event
    # payload = event['body']
    # data = HomeWidget.from_json(payload)
    user_id = getUserId(event)
    payload = json.loads(event['body'])
    widget_ids = payload['widgetIds']
    print("Data received: ", widget_ids)

    # Query the home widgets table
    results = []
    request_items = {
        homeWidgetsDb.name: {
            'Keys': [{'id': widget_id} for widget_id in widget_ids]
        }
    }
    response = dynamoDb.batch_get_item(RequestItems=request_items)
    results = response['Responses'][homeWidgetsDb.name]

    # TODO: VALIDATIONS NEEDED 1. user_id should be present in the payload 2. if not, the user should be in access list


    if not results:
            return {"statusCode": 404, "body": json.dumps("Widgets not found with Id " + str(widget_ids))}
    return {
        "statusCode": 200,
        "body": json.dumps(results, cls=DecimalEncoder)
    }

