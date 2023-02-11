import nacl.pwhash


def hash(input: str, format: str = 'UTF-8'):
    hashed_password = nacl.pwhash.argon2id.str(bytes(input, format))
    return hashed_password.decode(format)
