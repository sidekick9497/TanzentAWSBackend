import json
import logging
import uuid

from models import Line
from models import LineProperty
from utils import getDBConnection, getUserId
from values import configs

logging.basicConfig(level=logging.INFO)


def save_line_to_db(table, saved_line: Line):
    print("saving the lines to DB")
    table.put_item(
        Item={
            "lineId": saved_line.line_id,
            "title": saved_line.title,
            "userId": str(saved_line.user_id),
            "createdAt": str(saved_line.created_at),
            "visibility": saved_line.visibility,
            "shortText": saved_line.short_text,
            "sharedTo": saved_line.shared_to
        }
    )


def save_line_property_to_db(table, properties: LineProperty):
    logging.info("saving the lines property to DB")
    table.put_item(
        Item={
            "lineId": properties.line_id,
            "content": properties.content,
            "hideOnRead": properties.hide_on_read,
            #TODO: Not implemented, setting the property defaults, "deleteOnRead": properties.delete_on_read,
            # "readBy": properties.read_by
            "containsPrivateLines": properties.contains_private_lines
        }
    )


def createStringListForDB(shared_to):
    # create a list of maps with key as "S" and value iterated for shared_to list
    return [{"S": x} for x in shared_to]


def lambda_handler(event, context):
    dynamodb = getDBConnection()

    try:


        line_id = None
        saved_line = None
        request_body = json.loads(event['body'])
        print(request_body)
        is_line_present = 'line' in request_body
        is_properties_present = "lineProperties" in request_body
        if not is_line_present and not is_properties_present:
            logging.warning("invalid request body in the passed event")
            return {"statusCode": 400, "body": "Invalid request body"}

        if is_line_present:
            line = request_body['line']
            print(line)
            print("lineId" in line)
            title = line['title']
            user_id = getUserId(event)
            created_at = line['createdAt']
            visibility = line['visibility']
            if 'shortText' in line:
                short_text = line['shortText']
            else:
                short_text = "short_text not present"
            if "lineId" not in line or line['lineId'] == "":
                print("lineId not present")
                line_id = str(uuid.uuid4())
            else:
                line_id = line['lineId']
            shared_to = []
            if "sharedTo" in line:
                shared_to = (line['sharedTo'])
                print("shared_to  : " + str(shared_to))
            saved_line = Line(title, user_id, line_id, created_at, visibility, short_text, shared_to)

            lines_table = dynamodb.Table(configs.LINES_TABLE_NAME)
            save_line_to_db(lines_table, saved_line)
            print("savedLine")


        # Check if we have line_properties in the body and save it to the DB
        if is_properties_present:
            properties_object = request_body['lineProperties']
            content = properties_object['content']
            hide_on_read = properties_object['hideOnRead']
            delete_on_read = properties_object['deleteOnRead']
            contains_private_lines = properties_object['containsPrivateLines']
            if line_id is None and line_id not in properties_object:
                return {"statusCode": 400, "body": "Line_id should be present if only properties are passed"}
            if not is_line_present:
                line_id = properties_object['lineId']
            print("LineId created from UUID" + str(line_id))
            line_properties: LineProperty = LineProperty(line_id, content, hide_on_read, delete_on_read, [],
                                                         contains_private_lines)
            property_table = dynamodb.Table(configs.LINES_PROPERTY_TABLE_NAME)
            save_line_property_to_db(property_table, line_properties)
            print("savedProperties: ", str(line_properties))

        return {"statusCode": 200, "body": json.dumps(line_id)}
    except Exception as e:
        print(e)
        return {"statusCode": 500, "body": json.dumps("Error reading items: " + str(e))}
