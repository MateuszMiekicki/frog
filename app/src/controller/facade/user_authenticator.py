def authenticate(user, token_builder):
    if user:
        return {'access_token': token_builder.encode_token(user), 'token_type': 'bearer'}
    return None
