import json

from models import Line, LineProperty, PrivateLines
from utils import getDBConnection, getUserIdFromToken
from values import configs


def lambda_handler(event, context):
    # Initialize the DynamoDB client
    dynamodb = getDBConnection()
    lines_db = dynamodb.Table(configs.LINES_TABLE_NAME)
    lines_properties_db = dynamodb.Table(configs.LINES_PROPERTY_TABLE_NAME)

    try:
        user_id = getUserIdFromToken(event)
        #TODO: Add the access level check

        # Extract the path parameters from the url
        line_id = event["pathParameters"]["lineId"]

        if line_id is None:
            return {"statusCode": 502, "body": "lineId not found"}
        # Get the line item from the DynamoDB
        lines_db_response = lines_db.get_item(
            Key={
                "lineId": line_id
            }
        )
        # get the line properties from the DynamoDB
        lines_properties_db_response = lines_properties_db.get_item(Key={
            "lineId": line_id
        })
        line: Line = lines_db_response["Item"]
        line_properties = lines_properties_db_response["Item"]
        private_lines = line_properties["privateLines"]
        content = line_properties["content"]
        ##TODO: disabled logic for hide_private_lines
        ##updated_content = hide_private_lines(content, private_lines, 10)
        line_properties["content"] = content;
        response = {"line": line, "properties": line_properties}
        return {"statusCode": 200, "body": json.dumps(response)}
    except Exception as e:
        print(e)
        return {"statusCode": 500, "body": json.dumps("Error reading items: " + str(e))}


def hide_private_lines(content, private_lines, user_id):
    for private_line in private_lines:
        if user_id not in private_line["userIds"]:
            length = int(private_line["length"])
            from_offset = int(private_line["fromOffset"])
            replacement_string = "*" * length
            content = (
                    content[:from_offset]
                    + replacement_string
                    + content[from_offset + length:]
            )
    return content
