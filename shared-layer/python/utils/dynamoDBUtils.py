import boto3
import os


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
