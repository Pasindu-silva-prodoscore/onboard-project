from .. import db
import hashlib
import hmac
import os
import base64

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    @classmethod
    def get_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def create(cls, username, password):
        user = cls(
            username=username,
            password_hash=cls.generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        return user
    
    @staticmethod
    def generate_password_hash(password, iterations=100000):
        """Generate a custom password hash using PBKDF2-HMAC-SHA256."""
        salt = os.urandom(16)
        password_bytes = password.encode('utf-8')
        key = hashlib.pbkdf2_hmac('sha256', password_bytes, salt, iterations, dklen=32)
        salt_b64 = base64.b64encode(salt).decode('ascii')
        key_b64 = base64.b64encode(key).decode('ascii')
        return f"pbkdf2-sha256${salt_b64}${iterations}${key_b64}"

    @staticmethod
    def verify_password(stored_hash, password):
        """Verify a password against the stored hash."""
        try:
            algorithm, salt_b64, iterations, key_b64 = stored_hash.split('$')
            if algorithm != 'pbkdf2-sha256':
                return False
            salt = base64.b64decode(salt_b64)
            expected_key = base64.b64decode(key_b64)
            iterations = int(iterations)
            password_bytes = password.encode('utf-8')
            computed_key = hashlib.pbkdf2_hmac('sha256', password_bytes, salt, iterations, dklen=32)
            return hmac.compare_digest(expected_key, computed_key)
        except (ValueError, TypeError):
            return False