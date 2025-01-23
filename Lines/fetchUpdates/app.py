import json
from datetime import datetime

from utils import getDBConnection
from utils.dynamoDBUtils import update_user_visitor_count, DecimalEncoder
from values import configs


def lambda_handler(event, context):
    # Use the DynamoDB client instead of the table resource for batch_get_item
    dynamoDb = getDBConnection()
    circleDb = dynamoDb.Table(configs.CIRCLES_TABLE_NAME)
    linesDb = dynamoDb.Table(configs.LINES_TABLE_NAME)
    # Get the payload from event
    payload = json.loads(event['body'])
    # Get the list of ids from circles key
    print("Data received: ", payload)
    circle_id = payload['circleId']
    client_last_updated = payload['updatedAt']

    # Fetch the circle last update time
    response = circleDb.get_item(Key={'circleId': circle_id})
    print("Response: ", response)
    if 'Item' not in response:
        return {"statusCode": 404, "body": json.dumps("Circles not found with Id " + str(circle_id))}
    circle = response['Item']
    print("Circle: ", circle)
    if ('updatedAt' not in circle) or (circle['updatedAt'] is None):
        user_last_updated = 0
    else:
        user_last_updated = circle['updatedAt']

    circle['updatedAt'] = int(user_last_updated)
    update_user_visitor_count(circle_id)

    # Check if the client is outdated
    if user_last_updated > client_last_updated:
        # TODO: Fetch the updated circles
        return {
            "statusCode": 200,
            "body": json.dumps({"outdated": True, "data": circle}, cls=DecimalEncoder)
        }
    else:
        return {
            "statusCode": 200,
            "body": json.dumps({"outdated": False, "data": circle}, cls=DecimalEncoder)
        }
