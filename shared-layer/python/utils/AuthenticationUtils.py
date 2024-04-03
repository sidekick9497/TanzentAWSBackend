
def validate_token(event):
    # Try to extract the Authorization header
    token = event.get('headers', {}).get('Authorization')
    if token:
        #//TODO: add more validation afterwards
        return True
    return False


def getUserIdFromToken(event):
    if not validate_token(event):
        return None

    token = event.get('headers', {}).get('Authorization')
    if token:
        if token.startswith("Bearer "):
            token = token[7:]
        return token
    return None
