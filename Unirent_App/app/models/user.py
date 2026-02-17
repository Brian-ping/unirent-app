from bson.objectid import ObjectId
from itsdangerous import URLSafeTimedSerializer
from werkzeug.security import generate_password_hash
from flask import current_app

class User:
    @staticmethod
    def get_collection():
        """Get the user collection from Flask app"""
        return current_app.user_collection  # Matches your exact setup

    @staticmethod
    def find_by_email(email):
        """Find user by email"""
        return User.get_collection().find_one({'email': email})

    @staticmethod
    def create(full_name, email, contact_number, id_number, password):
        """Create new user"""
        return User.get_collection().insert_one({
            'full_name': full_name,
            'email': email,
            'contact_number': contact_number,
            'id_number': id_number,
            'password': password
        })

    @staticmethod
    def generate_reset_token(user_id):
        """Generate password reset token (1 hour expiration)"""
        serializer = URLSafeTimedSerializer(current_app.secret_key)
        return serializer.dumps(str(user_id), salt='password-reset')

    @staticmethod
    def verify_reset_token(token, max_age=3600):
        """Verify reset token and return user if valid"""
        serializer = URLSafeTimedSerializer(current_app.secret_key)
        try:
            user_id = serializer.loads(token, salt='password-reset', max_age=max_age)
            return User.get_collection().find_one({'_id': ObjectId(user_id)})
        except:
            return None

    @staticmethod
    def update_password(user_id, new_password):
        """Update user password and clear reset token"""
        User.get_collection().update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'password': new_password}}
        )