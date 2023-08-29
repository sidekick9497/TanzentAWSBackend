import json
import boto3

from models import Line, LineProperty, PrivateLines
from utils import getDBConnection
from values import configs


def lambda_handler(event, context):
    # Initialize the DynamoDB client
    dynamodb = getDBConnection()
    lines_db = dynamodb.Table(configs.LINES_TABLE_NAME)
    lines_properties_db = dynamodb.Table(configs.LINES_PROPERTY_TABLE_NAME)

    try:
        line_id = event["pathParameters"]["lineId"]
        user_id = event["pathParameters"]["userId"]
        if line_id is None or user_id is None:
            return {"statusCode": 502, "body": "lineId or userId not found"}
        lines_db_response = lines_db.get_item(
            Key={
                'lineId': line_id,
                'userId': user_id
            }
        )

        lines_properties_db_response = lines_properties_db.get_item(Key={
            "lineId": line_id
        })
        line: Line = lines_db_response["Item"]
        line_properties: LineProperty = lines_properties_db_response["Item"]
        response = {"line": line, "properties": line_properties}
        return {"statusCode": 200, "body": json.dumps(response)}
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps("Error reading items: " + str(e))}
