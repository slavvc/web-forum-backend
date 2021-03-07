from hashlib import sha512
import secrets
import string

ALPHABET = (string.digits + string.ascii_letters).encode('ascii')


def make_token():
    return secrets.token_urlsafe(512)


def make_salt():
    letters = [
        secrets.choice(ALPHABET)
        for _ in range(512)
    ]
    return bytes(letters)


def make_password(password: str) -> (str, str):
    salt = make_salt()
    hasher = sha512()
    hasher.update(password.encode('ascii'))
    hasher.update(salt)
    password_hash = hasher.hexdigest()
    return password_hash, salt.decode('ascii')


def check_password(
    password: str, 
    password_hash: str, 
    password_salt: str
) -> bool:
    hasher = sha512()
    hasher.update(password.encode('ascii'))
    hasher.update(password_salt.encode('ascii'))
    digest = hasher.hexdigest()
    return digest == password_hash


def password_is_good(password: str):
    return len(password) < 256 and all(
        ord(c) in ALPHABET
        for c in password
    )
