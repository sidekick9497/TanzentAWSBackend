import json
from _decimal import Decimal
from http.client import responses

import boto3
from boto3.dynamodb.conditions import Key

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
    widget_ids = []
    if 'widgetIds' in payload:
        widget_ids = payload['widgetIds']
    user_id_for_widgets = ""
    if 'userId' in payload:
        user_id_for_widgets = payload['userId']
    print("Data received: ", widget_ids, user_id_for_widgets)
    # Fetch widgets by userId if widget_ids are not provided
    if  len(widget_ids) == 0:
        if (user_id_for_widgets is None) or (user_id_for_widgets == ""):
            return {"statusCode": 400, "body": json.dumps("userId / widgetIds are required to fetch widgets")}
        response = homeWidgetsDb.query(
            IndexName='UserId_Index',  # Assuming there's a GSI on userId
            KeyConditionExpression=Key('userId').eq(user_id_for_widgets)
        )
        results = response['Items']
        if not results:
            return {"statusCode": 404, "body": json.dumps("No widgets found for userId " + str(user_id_for_widgets))}
        return {
            "statusCode": 200,
            "body": json.dumps(results, cls=DecimalEncoder)
        }

    # Query the home widgets table using the provided widget_ids
    results = []
    request_items = {
        homeWidgetsDb.name: {
            'Keys': [{'id': widget_id} for widget_id in widget_ids]
        }
    }
    print("Request Items: ", request_items)
    try:
        response = dynamoDb.batch_get_item(RequestItems=request_items)
        results = response['Responses'][homeWidgetsDb.name]
    except Exception as e:
        print(e)
        return {"statusCode": 500, "body": json.dumps("Error reading items: " + str(e))}
    print("Response: ", response)
    results = response['Responses'][homeWidgetsDb.name]

    # TODO: VALIDATIONS NEEDED 1. user_id should be present in the payload 2. if not, the user should be in access list


    if not results:
            return {"statusCode": 404, "body": json.dumps("Widgets not found with Id " + str(widget_ids))}
    return {
        "statusCode": 200,
        "body": json.dumps(results, cls=DecimalEncoder)
    }

