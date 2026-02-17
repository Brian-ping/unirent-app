from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from app.models.user import User
from app.utils.email import send_reset_email
from bson.objectid import ObjectId
from bson.errors import InvalidId
import logging
from itsdangerous import SignatureExpired, BadSignature

logger = logging.getLogger(__name__)

class AuthController:
    @staticmethod
    def register(full_name, email, contact_number, id_number, password):
        """
        Registers a new user with proper validation and password hashing.
        
        Args:
            full_name: User's full name
            email: User's email address
            contact_number: User's phone number
            id_number: User's identification number
            password: Plain text password
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            # Validate input
            if not all([full_name, email, contact_number, id_number, password]):
                return False, "All fields are required"
                
            if len(password) < 8:
                return False, "Password must be at least 8 characters"
                
            if User.find_by_email(email):
                return False, "Email already registered"

            # Create user
            hashed_password = generate_password_hash(
                password,
                method='pbkdf2:sha256',
                salt_length=16
            )
            
            user_id = User.create(
                full_name=full_name,
                email=email,
                contact_number=contact_number,
                id_number=id_number,
                password=hashed_password
            )
            
            if not user_id:
                raise Exception("User creation failed")
                
            logger.info(f"New user registered: {email} (ID: {user_id})")
            return True, "Registration successful"
            
        except Exception as e:
            logger.error(f"Registration error for {email}: {str(e)}", exc_info=True)
            return False, "Registration failed. Please try again."

    @staticmethod
    def login(email, password):
        """
        Authenticates a user with secure password verification.
        
        Args:
            email: User's email address
            password: Plain text password
            
        Returns:
            tuple: (user: dict/None, message: str)
        """
        try:
            user = User.find_by_email(email)
            if not user:
                return None, "Invalid email or password"
            
            if not check_password_hash(user['password'], password):
                return None, "Invalid email or password"
                
            # Sanitize user data before returning
            user_data = {
                '_id': str(user['_id']),
                'full_name': user['full_name'],
                'email': user['email'],
                'contact_number': user['contact_number']
            }
            
            return user_data, "Login successful"
            
        except Exception as e:
            logger.error(f"Login error for {email}: {str(e)}", exc_info=True)
            return None, "Login failed. Please try again."

    @staticmethod
    def reset_password(email):
        """
        Initiates a password reset process.
        
        Args:
            email: User's email address
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            user = User.find_by_email(email)
            if not user:
                # Return true to prevent email enumeration attacks
                return True, "If this email exists, a reset link has been sent"
            
            token = User.generate_reset_token(str(user['_id']))
            send_reset_email(email, token)
            
            logger.info(f"Password reset initiated for {email}")
            return True, "If this email exists, a reset link has been sent"
            
        except Exception as e:
            logger.error(f"Password reset error for {email}: {str(e)}", exc_info=True)
            return False, "Password reset failed. Please try again."

    @staticmethod
    def verify_reset_token(token):
        """
        Verifies a password reset token.
        
        Args:
            token: Reset token sent to user's email
            
        Returns:
            tuple: (user_id: str/None, message: str)
        """
        try:
            user = User.verify_reset_token(token)
            if not user:
                return None, "Invalid or expired reset link"
            return str(user['_id']), "Token is valid"
        except SignatureExpired:
            return None, "Reset link has expired"
        except (BadSignature, InvalidId):
            return None, "Invalid reset link"
        except Exception as e:
            logger.error(f"Token verification error: {str(e)}", exc_info=True)
            return None, "Token verification failed"

    @staticmethod
    def update_password(token, new_password):
        """
        Updates user's password after token verification.
        
        Args:
            token: Reset token
            new_password: New plain text password
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            if len(new_password) < 8:
                return False, "Password must be at least 8 characters"
                
            # Verify token and get user
            user_id, message = AuthController.verify_reset_token(token)
            if not user_id:
                return False, message
                
            # Update password
            hashed_password = generate_password_hash(
                new_password,
                method='pbkdf2:sha256',
                salt_length=16
            )
            
            User.update_password(user_id, hashed_password)
            logger.info(f"Password updated for user {user_id}")
            return True, "Password updated successfully"
            
        except Exception as e:
            logger.error(f"Password update error: {str(e)}", exc_info=True)
            return False, "Password update failed. Please try again."

    @staticmethod
    def logout():
        """
        Placeholder for logout functionality.
        Actual session clearing should happen in routes.
        """
        return True, "Logout successful"