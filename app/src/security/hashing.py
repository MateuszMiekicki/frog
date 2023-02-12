import nacl.pwhash


def hash(input: str, format: str = 'UTF-8') -> str:
    hashed_password = nacl.pwhash.argon2id.str(bytes(input, format))
    return hashed_password.decode(format)


def verify(password_hash: str, password: str, format: str = 'UTF-8') -> bool:
    try:
        return nacl.pwhash.verify(bytes(password_hash, format),
                                  bytes(password, format))
    except nacl.exceptions.InvalidkeyError as err:
        return False
