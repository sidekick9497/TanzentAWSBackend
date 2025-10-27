import os


def validate_token(event):
    # Try to extract the Authorization header
    token = event.get('headers', {}).get('Authorization')
    if token:
        #//TODO: add more validation afterwards
        return True
    return False


def getUserId(event):
    print(event)
    # Access claims through the JWT authorizer path
    claims = event['requestContext']['authorizer']['jwt']['claims']

    # Extract the phone number from the claims
    phone_number = claims.get('phone_number', None)

    # If phone_number is not directly available, check the firebase identities
    if not phone_number and 'firebase' in claims:
        try:
            # The firebase field appears to be a string representation of a dict
            import ast
            firebase_data = ast.literal_eval(claims['firebase'])
            if 'identities' in firebase_data and 'phone' in firebase_data['identities']:
                phone_number = firebase_data['identities']['phone'][0]
        except:
            pass

    return phone_number





