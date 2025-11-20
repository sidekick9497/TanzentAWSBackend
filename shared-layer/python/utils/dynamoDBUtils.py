import json
from _decimal import Decimal
from datetime import datetime

import boto3
import os
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


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)
