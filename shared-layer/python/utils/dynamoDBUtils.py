import json
from _decimal import Decimal
from datetime import datetime

import boto3
import os

from models.LineVisibility import get_db_mapped_visibility
from values import configs


def getDBConnection():
    """
        Gets the connection to the DynamoDB dependence on the environment of the server

        Make sure that the docker container of dynamoDB is running at 8080, to successfully connect in local
    """
    if os.environ.get("AWS_SAM_LOCAL"):
        print("connected to local db")
        dynamodb = boto3.resource("dynamodb", endpoint_url="http://host.docker.internal:8000")
    else:
        dynamodb = boto3.resource("dynamodb")
    return dynamodb


def update_user_updated_at(user_id, updated_at):
    """
    DEPRECATED: This function is kept for backward compatibility.
    The functionality has been merged into update_user_view_count and update_user_visitor_count.
    """
    table = getDBConnection().Table(configs.CIRCLES_TABLE_NAME)
    table.update_item(
        Key={'circleId': user_id},
        UpdateExpression="set updatedAt = :val",
        ExpressionAttributeValues={':val': updated_at}
    )


def update_user_view_count(user_id):
    """
    Update the view count and last updated timestamp for a user in a single operation.
    
    Args:
        user_id (str): The ID of the user to update
        
    Returns:
        str: The ISO formatted timestamp when the update occurred
    """
    table = getDBConnection().Table(configs.CIRCLES_TABLE_NAME)
    now = int(datetime.now().timestamp() * 1_000)
    
    table.update_item(
        Key={'circleId': user_id},
        UpdateExpression="""
            SET lineViews = if_not_exists(lineViews, :zero) + :one,
                updatedAt = :now
        """,
        ExpressionAttributeValues={
            ':zero': 0,
            ':one': 1,
            ':now': now
        }
    )
    return now


def update_user_visitor_count(user_id):
    """
    Update the visitor count and last updated timestamp for a user in a single operation.
    
    Args:
        user_id (str): The ID of the user to update
        
    Returns:
        str: The ISO formatted timestamp when the update occurred
    """
    table = getDBConnection().Table(configs.CIRCLES_TABLE_NAME)
    now = int(datetime.now().timestamp() * 1_000)
    
    table.update_item(
        Key={'circleId': user_id},
        UpdateExpression="""
            SET visits = if_not_exists(visits, :zero) + :one,
                updatedAt = :now
        """,
        ExpressionAttributeValues={
            ':zero': 0,
            ':one': 1,
            ':now': now
        }
    )
    return now

def update_user_line_counters(user_id, is_update, line_id, new_visibility):
    user_table = getDBConnection().Table(configs.CIRCLES_TABLE_NAME)
    lines_table = getDBConnection().Table(configs.LINES_TABLE_NAME)

    # Convert new visibility to clean form
    clean_new = get_db_mapped_visibility(new_visibility)

    old_visibility = None
    clean_old = None

    print("called counter update " + str(is_update) + " " + str(line_id) + " " + str(new_visibility))

    # 1. Fetch old visibility only when updating
    if is_update:
        resp = lines_table.get_item(Key={"lineId": line_id})
        old_item = resp.get("Item")

        if not old_item:
            print("Line not found during update. Skipping counter update.")
            return

        old_visibility = old_item.get("visibility")
        if new_visibility == old_visibility:
            return
        clean_old = get_db_mapped_visibility(old_visibility)


    # 2. Build increment map using CLEAN visibility keys
    inc_map = {}

    if not is_update:
        # Creation: add to total + new bucket
        inc_map["totalLines"] = 1
        inc_map[f"{clean_new}Lines"] = 1
    else:
        # Update: decrement old bucket, increment new bucket
        inc_map[f"{clean_old}Lines"] = -1
        inc_map[f"{clean_new}Lines"] = 1

    # 3. Build safe placeholder expressions
    expr_parts = []
    values = {}

    for key, val in inc_map.items():
        ph = f":inc_{key}"
        expr_parts.append(f"{key} {ph}")
        values[ph] = val

    update_expr = "ADD " + ", ".join(expr_parts)

    # 4. Atomic update in user table
    user_table.update_item(
        Key={"circleId": user_id},
        UpdateExpression=update_expr,
        ExpressionAttributeValues=values
    )



class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)
