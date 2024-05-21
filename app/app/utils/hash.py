import hashlib
import secrets

def hash_password(password):
    # Generar una sal aleatoria
    salt = secrets.token_hex(16)
    salted_password = password + salt
    hashed_password = hashlib.sha256(salted_password.encode()).hexdigest()
    return hashed_password, salt

def verify_password(password, hashed_password, salt):
   
    salted_password = password + salt
    calculated_hash = hashlib.sha256(salted_password.encode()).hexdigest()
    return calculated_hash == hashed_password