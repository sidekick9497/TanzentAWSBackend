import json
import logging
from models import Line, PrivateLines, LineProperty
from utils import getDBConnection, getUserIdFromToken
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
        # Check if lineId is present in the path parameters
        if "pathParameters" not in event or "lineId" not in event["pathParameters"]:
            logging.error("Missing lineId in path parameters")
            return {"statusCode": 400, "body": json.dumps({"message": "Missing lineId in path parameters"})}

        line_id = event["pathParameters"]["lineId"]
        logging.info(f"{line_id} is sent for deletion")

        table = dynamodb.Table(configs.LINES_TABLE_NAME)

        # Check if the item exists before attempting to delete
        response = table.get_item(Key={"lineId": line_id})
        if "Item" not in response:
            logging.warning(f"Line with lineId {line_id} not found")
            return {"statusCode": 404, "body": json.dumps({"message": "Line not found"})}

        # Attempt to delete the item
        table.delete_item(Key={"lineId": line_id})
        logging.info(f"Line with lineId {line_id} successfully deleted")
        return {"statusCode": 200, "body": json.dumps({line_id: "deleted"})}

    except Exception as e:
        logging.error(f"Error deleting item: {str(e)}", exc_info=True)
        return {"statusCode": 500, "body": json.dumps({"message": "Error deleting item", "error": str(e)})}
