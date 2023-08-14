import json
import boto3
from utils import getDBConnection


def lambda_handler(event, context):
    # Initialize the DynamoDB client
    dynamodb = getDBConnection()
    table_name = "LinesDB"
    table = dynamodb.Table(table_name)

    try:
        line_id = event["pathParameters"]["lineId"]
        if line_id is None:
            return {"statusCode": 502, "body": "invalid line id passed"}

        response = table.get_item(Key={"lineId": line_id})
        print(response)
        items = response["Item"]
        return {"statusCode": 200, "body": json.dumps(items)}
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps("Error reading items: " + str(e))}
