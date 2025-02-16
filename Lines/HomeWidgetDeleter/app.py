import json
import logging
from datetime import datetime

from models import Line, PrivateLines, LineProperty
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
        # Check if lineId is present in the path parameters
        if "pathParameters" not in event or "id" not in event["pathParameters"]:
            logging.error("Missing widgetId in path parameters")
            return {"statusCode": 400, "body": json.dumps({"message": "Missing lineId in path parameters"})}
        user_id = getUserId(event)
        widget_id = event["pathParameters"]["id"]
        logging.info(f"{widget_id} is sent for deletion")

        table = dynamodb.Table(configs.HOME_WIDGETS_TABLE_NAME)

        # Check if the item exists before attempting to delete
        response = table.get_item(Key={"id": widget_id})
        if "Item" not in response:
            logging.warning(f"Line with lineId {widget_id} not found")
            return {"statusCode": 404, "body": json.dumps({"message": "Line not found"})}

        # TODO: The line should belong to the current user first before deleting
        # Attempt to delete the item
        table.delete_item(Key={"id": widget_id})
        logging.info(f"Line with lineId {widget_id} successfully deleted")
        update_user_updated_at(user_id, int(datetime.utcnow().timestamp() * 1_000))

        # Return a success response with the lineId
        return {"statusCode": 200, "body": json.dumps({widget_id: "deleted"})}

    except Exception as e:
        logging.error(f"Error deleting item: {str(e)}", exc_info=True)
        return {"statusCode": 500, "body": json.dumps({"message": "Error deleting item", "error": str(e)})}
