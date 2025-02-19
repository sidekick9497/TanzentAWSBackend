import json

from models import Line, LineProperty, PrivateLines
from utils import getDBConnection, getUserId
from utils.dynamoDBUtils import update_user_view_count
from values import configs


def lambda_handler(event, context):
    # Initialize the DynamoDB client
    dynamodb = getDBConnection()
    lines_db = dynamodb.Table(configs.LINES_TABLE_NAME)
    lines_properties_db = dynamodb.Table(configs.LINES_PROPERTY_TABLE_NAME)
    circles_db = dynamodb.Table(configs.CIRCLES_TABLE_NAME)

    try:
        user_id = getUserId(event)

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
        # TODO: Add access level check to see if the user has access to the line

        # get the line properties from the DynamoDB
        lines_properties_db_response = lines_properties_db.get_item(Key={
            "lineId": line_id
        })
        line: Line = lines_db_response["Item"]
        print("Line: ", line)
        line_properties = lines_properties_db_response["Item"]
        print("Line properties: ", line_properties)
        content = line_properties["content"]
        updated_content = hide_private_lines(content, line_properties['containsPrivateLines'], user_id, line["userId"])
        if user_id != line["userId"]:
            update_user_view_count(line["userId"])
        print("Updated content: ", updated_content)
        line_properties["content"] = updated_content
        response = {"line": line, "properties": line_properties}
        return {"statusCode": 200, "body": json.dumps(response)}
    except Exception as e:
        print(e)
        return {"statusCode": 500, "body": json.dumps("Error reading items: " + str(e))}


def hide_private_lines(content, has_private_lines, requester_id, line_owner_id):
    print("requester_id: ", requester_id, "line_owner_id: ", line_owner_id)
    if requester_id == line_owner_id:
        return content
    print("Has private lines: ", has_private_lines)
    if has_private_lines:
        # Read the JSON data into a Python object
        content_data = json.loads(content)

        # Iterate through the list of content items
        for item in content_data:
            # Check if the 'privateLineSelector' attribute is set to True
            if 'attributes' in item and item['attributes'].get('privateLineSelector'):
                has_access = False
                if 'privateLine' in item['attributes']:
                    print("Private lines: ", item['attributes']['privateLine'])
                    has_access = requester_id in item['attributes']['privateLine']

                # Replace content with 'xxxx' if the user does not have access
                if not has_access:
                    item['insert'] = 'x' * len(item['insert'])
                #We need to remove the privateLine attribute if user doesn't has access
                if not has_access and 'privateLine' in item['attributes']:
                    del item['attributes']['privateLine']

        # Convert the modified content back to JSON
        content = json.dumps(content_data)

    return content
