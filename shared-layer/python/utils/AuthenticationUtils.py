import os


def validate_token(event):
    # Try to extract the Authorization header
    token = event.get('headers', {}).get('Authorization')
    if token:
        #//TODO: add more validation afterwards
        return True
    return False


def getUserId(event):
    if os.environ.get("AWS_SAM_LOCAL"):
        token = event.get('headers', {}).get('Authorization')
        if token:
            if token.startswith("Bearer "):
                token = token[7:]
            return token
        return None
    claims = event['requestContext']['authorizer']['claims']
    # Extract the phone number from the claims
    phone_number = claims.get('phone_number', None)
    return phone_number





