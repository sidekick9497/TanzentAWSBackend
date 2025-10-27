import json
import logging
from datetime import datetime

from models import Line, PrivateLines, LineProperty
from utils import getDBConnection, getUserId
from utils.dynamoDBUtils import update_user_updated_at
from values import configs

logging.basicConfig(level=logging.INFO)

"""

"""


def lambda_handler(event, context):
    dynamodb = getDBConnection()

    try:
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
            logging.warning(f"widget with id {widget_id} not found")
            return {"statusCode": 404, "body": json.dumps({"message": "widget not found"})}
        if response["Item"]["userId"] != user_id:
            return {"statusCode": 401, "body": json.dumps({"message": "Unauthorized access, the widget does not belong to the current user"})}
        # Attempt to delete the item
        table.delete_item(Key={"id": widget_id})
        logging.info(f"widget with lineId {widget_id} successfully deleted")
        update_user_updated_at(user_id, int(datetime.utcnow().timestamp() * 1_000))

        # Return a success response with the lineId
        return {"statusCode": 200, "body": json.dumps({widget_id: "deleted"})}

    except Exception as e:
        logging.error(f"Error deleting item: {str(e)}", exc_info=True)
        return {"statusCode": 500, "body": json.dumps({"message": "Error deleting item", "error": str(e)})}
