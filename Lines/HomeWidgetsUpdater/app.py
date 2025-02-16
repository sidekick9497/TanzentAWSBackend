import json
import uuid
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
    payload = event['body']
    data = HomeWidget.from_json(payload)
    print("Data received: ", data)

    # Insert/update into the home widgets table
    user_id = getUserId(event)
    if data.external_id is None or data.external_id == "":
        external_id = str(uuid.uuid4())
    else:
        external_id = data.external_id
    widget_data = data.widget_data
    widget_type = data.widget_type
    composite_id = data.composite_id
    is_widget_private = data.is_widget_private
    shared_to_circles = data.shared_to_circles
    widget_id = data.widget_id

    response = homeWidgetsDb.put_item(
        Item={
            "id": external_id,
            "userId": user_id,
            "widgetData": widget_data,
            "widgetType": widget_type,
            "compositeId": composite_id,
            "isWidgetPrivate": is_widget_private,
            "sharedToCircles": shared_to_circles,
            "widgetId": widget_id
        }
    )
    # TODO: VALIDATIONS NEEDED 1. user_id should be present in the payload 2. if not, the user should be in access list

    return {
        "statusCode": 200,
        "body": json.dumps({"id": external_id}, cls=DecimalEncoder)
    }