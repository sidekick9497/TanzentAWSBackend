import json
import logging
from datetime import datetime

from models import Line, PrivateLines, LineProperty
from models.LineVisibility import get_db_mapped_visibility
from utils import getDBConnection, getUserId
from utils.dynamoDBUtils import update_user_updated_at
from values import configs

logging.basicConfig(level=logging.INFO)

"""
A Lambda function to delete a line from DynamoDB using the lineId passed in the URL.
It takes an event and context as parameters.
Returns a dictionary with a status code and a JSON body indicating the result of the deletion.
"""


def lambda_handler(event, context):
    dynamodb = getDBConnection()

    try:
        if "pathParameters" not in event or "lineId" not in event["pathParameters"]:
            return {"statusCode": 400, "body": json.dumps({"message": "Missing lineId in path parameters"})}

        user_id = getUserId(event)
        line_id = event["pathParameters"]["lineId"]

        table = dynamodb.Table(configs.LINES_TABLE_NAME)
        response = table.get_item(Key={"lineId": line_id})

        if "Item" not in response:
            return {"statusCode": 404, "body": json.dumps({"message": "Line not found"})}

        if response["Item"]["userId"] != user_id:
            return {"statusCode": 401, "body": json.dumps({"message": "Unauthorized access"})}

        # --- Update counters BEFORE delete ---
        visibility = response["Item"]["visibility"]
        db_mapped_visibility = get_db_mapped_visibility(visibility)
        user_table = dynamodb.Table(configs.CIRCLES_TABLE_NAME)

        inc_map = {
            "totalLines": -1,
            f"{db_mapped_visibility}Lines": -1
        }

        expr = "ADD " + ", ".join(f"{k} :{k}" for k in inc_map)
        values = {f":{k}": v for k, v in inc_map.items()}

        user_table.update_item(
            Key={"circleId": user_id},
            UpdateExpression=expr,
            ExpressionAttributeValues=values
        )
        # --- End counter update ---

        table.delete_item(Key={"lineId": line_id})

        update_user_updated_at(user_id, int(datetime.utcnow().timestamp() * 1_000))

        return {"statusCode": 200, "body": json.dumps({line_id: "deleted"})}

    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"message": "Error deleting item", "error": str(e)})}
