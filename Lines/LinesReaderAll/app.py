import json
from datetime import datetime

from boto3.dynamodb.conditions import Key
from utils import getDBConnection, getUserId, decrypt_text
from utils.dynamoDBUtils import update_user_visitor_count, update_user_updated_at, DecimalEncoder
from values import configs

def lambda_handler(event, context):
    """Handle request to fetch all lines for a user."""
    try:
        # Initialize DynamoDB connection
        dynamodb = getDBConnection()
        table = dynamodb.Table(configs.LINES_TABLE_NAME)
        
        # Get user IDs from request
        user_id_to_fetch = event["pathParameters"]["userId"]
        requested_user_id = getUserId(event)
        
        print(f"Request from user {requested_user_id} for user {user_id_to_fetch}'s lines")
        
        # Update visitor count if it's not the user viewing their own lines
        if requested_user_id != user_id_to_fetch:
            try:
                update_user_visitor_count(user_id_to_fetch)
            except Exception as e:
                print(f"Error updating visitor metrics: {str(e)}")
                # Continue with the request even if metrics update fails
        
        # Query the lines
        response = table.query(
            IndexName='UserId_Index',
            KeyConditionExpression=Key('userId').eq(user_id_to_fetch)
        )
        
        items = response.get("Items", [])
        print(f"Found {len(items)} lines for user {user_id_to_fetch}")

        # Filter out private content if not the owner
        if requested_user_id != user_id_to_fetch:
            items = replace_hidden_items(items, requested_user_id)
        return {
            "statusCode": 200,
            "body": json.dumps(items, cls=DecimalEncoder),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            }
        }
    except Exception as e:
        print(f"Error in lambda_handler: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps(f"Error reading items: {str(e)}"),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            }
        }

def replace_hidden_items(data, requester_user_id):
    # Define a dummy item structure
    dummy_item = {
        'createdAt': None,
        'visibility': 'LineVisibility.hidden',
        'shortText': 'xxxx',
        'lineId': None,
        'sharedTo': [],
        'title': 'Hidden Content',
        'userId': None
    }

    # Iterate over each item in the list
    for i, item in enumerate(data):
        if item.get('visibility') == 'LineVisibility.public':
            continue
        # Check if visibility is private or if sharedTo does not contain requester_user_id
        if item.get('visibility') == 'LineVisibility.private' or requester_user_id not in item.get('sharedTo', []):
            # Replace with the dummy item, keeping the 'lineId' the same for identification purposes
            hidden_item = dummy_item.copy()
            hidden_item['lineId'] = item.get('lineId')
            hidden_item['createdAt'] = item.get('createdAt')
            hidden_item['userId'] = item.get('userId')
            data[i] = hidden_item

    return data

