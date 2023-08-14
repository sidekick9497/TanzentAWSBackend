import json
import boto3

from models import Line
from utils import getDBConnection


def lambda_handler(event, context):
    dynamodb = getDBConnection()
    table_name = "LinesDB"
    table = dynamodb.Table(table_name)

    try:
        user_id = event["pathParameters"]["user_id"]
        # Scan all items from the table
        response = table.query(
            KeyConditionExpression="userId = :uid",
            ExpressionAttributeValues={":uid": user_id}
        )

        # Extract the items from the response
        items = response["Items"]
        my_lines = Line("hello world", "userId1")
        print(my_lines.title)
        # Print or process the items
        for item in items:
            print(item)  # Modify this line as needed

        return {"statusCode": 200, "body": json.dumps(my_lines.title)}
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps("Error reading items: " + str(e))}
