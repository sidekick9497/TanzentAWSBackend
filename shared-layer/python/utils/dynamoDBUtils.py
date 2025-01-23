import json
from _decimal import Decimal

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
    table = getDBConnection().Table(configs.CIRCLES_TABLE_NAME)
    table.update_item(
        Key={
            'circleId': user_id
        },
        UpdateExpression="set updatedAt = :val",
        ExpressionAttributeValues={
            ':val': updated_at
        }
    )


def update_user_view_count(user_id):
    table = getDBConnection().Table(configs.CIRCLES_TABLE_NAME)
    table.update_item(
        Key={
            'circleId': user_id
        },
        UpdateExpression="set lineViews = if_not_exists(lineViews, :zero) + :one",
        ExpressionAttributeValues={
            ':zero': 0,
            ':one': 1
        }
    )


def update_user_visitor_count(user_id):
    table = getDBConnection().Table(configs.CIRCLES_TABLE_NAME)
    table.update_item(
        Key={
            'circleId': user_id
        },
        UpdateExpression="set visits = if_not_exists(visits, :zero) + :one",
        ExpressionAttributeValues={
            ':zero': 0,
            ':one': 1
        }
    )


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)
