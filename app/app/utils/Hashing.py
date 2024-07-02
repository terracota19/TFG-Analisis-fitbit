import hashlib
import secrets

class HashSHA_256 :

    """Hash Password with SHA-256"""
    def hash_password(password):
        salt = secrets.token_hex(16)
        salted_password = password + salt
        hashed_password = hashlib.sha256(salted_password.encode()).hexdigest()

        return hashed_password, salt
   
    """Verify Password checking whether hashes are equal"""
    def verify_password(password, hashed_password, salt):
        
        salted_password = password + salt
        calculated_hash = hashlib.sha256(salted_password.encode()).hexdigest()
        return calculated_hash == hashed_password