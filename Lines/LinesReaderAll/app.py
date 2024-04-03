import json

from boto3.dynamodb.conditions import Key

from utils import getDBConnection, getUserIdFromToken
from values import configs


def lambda_handler(event, context):
    dynamodb = getDBConnection()
    table = dynamodb.Table(configs.LINES_TABLE_NAME)

    try:
        user_id_to_fetch = event["pathParameters"]["userId"]
        print(user_id_to_fetch)
        requested_user_id = getUserIdFromToken(event)
        print(requested_user_id)
        print(user_id_to_fetch)
        # Scan all items from the table
        response = table.query(
            IndexName='UserId_Index',
            KeyConditionExpression=Key('userId').eq(user_id_to_fetch))

        # Extract the items from the response
        items = response["Items"]
        return {"statusCode": 200, "body": json.dumps(items)}
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps("Error reading items: " + str(e))}
