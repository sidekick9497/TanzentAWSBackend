import json
import boto3
from utils import getDBConnection, getUserId
from values import configs


def lambda_handler(event, context):
    # Use the DynamoDB client instead of the table resource for batch_get_item
    dynamoDb = getDBConnection()
    circleDb = dynamoDb.Table(configs.CIRCLES_TABLE_NAME)
    # Get the payload from event
    payload = json.loads(event['body'])
    # Get the payload object from the event and create an Circles Item to be inserted into the DB
    circle = payload['circle']
    circle_name = circle['circleName']
    circle_quote = circle['quote']
    circle_display_picture = circle['displayPicture']
    circle_id = getUserId(event)

    print("Data received: ", circle_id, circle_name, circle_quote, circle_display_picture)
    try:
        response = circleDb.put_item(
            Item={
                "circleId": circle_id,
                "name": circle_name,
                "quote": circle_quote,
                "displayPicture": circle_display_picture
            }
        )
        print("Response is : ", response)
    except Exception as e:
        print(e)
        return {"statusCode": 500, "body": json.dumps("Error reading items: " + str(e))}
    return {
        "statusCode": 200,
        "body": json.dumps({"response": "success"})
    }
