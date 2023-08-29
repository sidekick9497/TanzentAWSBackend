import json

from boto3.dynamodb.conditions import Key

from utils import getDBConnection
from values import configs


def lambda_handler(event, context):
    dynamodb = getDBConnection()
    table = dynamodb.Table(configs.LINES_TABLE_NAME)

    try:
        user_id = str(event["pathParameters"]["userId"])
        print(user_id)
        # Scan all items from the table
        response = table.query(KeyConditionExpression=Key('userId').eq(user_id)
)

        # Extract the items from the response
        items = response["Items"]
        return {"statusCode": 200, "body": json.dumps(items)}
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps("Error reading items: " + str(e))}
