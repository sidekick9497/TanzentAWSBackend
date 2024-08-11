import json
import boto3
from utils import getDBConnection, getUserIdFromToken
from values import configs


def lambda_handler(event, context):
    # Use the DynamoDB client instead of the table resource for batch_get_item
    dynamoDb = getDBConnection()
    circleDb = dynamoDb.Table(configs.CIRCLES_TABLE_NAME)
    # Get the payload from event
    payload = json.loads(event['body'])
    # Get the list of ids from circles key
    circle_ids = payload['circles']
    print("Circles Ids passed",circle_ids)

    # Preparing the request items for the BatchGetItem call
    try:
        results = []
        for circle_id in circle_ids:
            response = circleDb.get_item(
                Key={
                    "circleId": circle_id
                }
            )
            print("Response is : ", response)
            #TODO: Remove the contacts object from either the response or the item
            if "Item" in response:
                results.append(response['Item'])
        print("Results from DB:", results)
        if (len(results) == 0):
            return {"statusCode": 404, "body": json.dumps("Circles not found with Id " + str(circle_ids))}

    except Exception as e:
        print(e)
        return {"statusCode": 500, "body": json.dumps("Error reading items: " + str(e))}
    return {
        "statusCode": 200,
        "body": json.dumps(results)
    }
