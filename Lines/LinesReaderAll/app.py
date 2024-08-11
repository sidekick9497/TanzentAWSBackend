import json

from boto3.dynamodb.conditions import Key, Attr

from utils import getDBConnection, getUserIdFromToken
from values import configs


def lambda_handler(event, context):
    dynamodb = getDBConnection()
    table = dynamodb.Table(configs.LINES_TABLE_NAME)

    try:
        user_id_to_fetch = event["pathParameters"]["userId"]
        print(user_id_to_fetch)
        requested_user_id = getUserIdFromToken(event)
        print(requested_user_id)
        print(user_id_to_fetch)
        print("Self user request", user_id_to_fetch)
        response = table.query(
            IndexName='UserId_Index',
            KeyConditionExpression=Key('userId').eq(user_id_to_fetch))

        items = response["Items"]
        print("Response all lines: ", items)

        if requested_user_id != user_id_to_fetch:
            items = replace_hidden_items(items, requested_user_id)

        return {"statusCode": 200, "body": json.dumps(items)}
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps("Error reading items: " + str(e))}

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

