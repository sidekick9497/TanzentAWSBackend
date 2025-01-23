import json
from _decimal import Decimal

import boto3
from utils import getDBConnection, getUserId
from utils.dynamoDBUtils import DecimalEncoder
from values import configs


def lambda_handler(event, context):
    # Use the DynamoDB client instead of the table resource for batch_get_item
    dynamoDb = getDBConnection()
    circleDb = dynamoDb.Table(configs.CIRCLES_TABLE_NAME)
    # Get the payload from event
    payload = json.loads(event['body'])
    # Get the list of ids from circles key
    circle_ids = payload['circles']
    print("Circles Ids passed", circle_ids)

    # Split the circle_ids into chunks of 100 or less
    chunk_size = 100
    chunks = [circle_ids[i:i + chunk_size] for i in range(0, len(circle_ids), chunk_size)]

    results = []
    for chunk in chunks:
        # Prepare the request items for the BatchGetItem call
        request_items = {
            circleDb.name: {
                'Keys': [{'circleId': circle_id} for circle_id in chunk]
            }
        }

        try:
            response = dynamoDb.batch_get_item(RequestItems=request_items)
            chunk_results = response['Responses'][circleDb.name]
            results.extend(chunk_results)
        except Exception as e:
            print(e)
            return {"statusCode": 500, "body": json.dumps("Error reading items: " + str(e))}

    if not results:
        return {"statusCode": 404, "body": json.dumps("Circles not found with Id " + str(circle_ids))}

    return {
        "statusCode": 200,
        "body": json.dumps(results, cls=DecimalEncoder)
    }


