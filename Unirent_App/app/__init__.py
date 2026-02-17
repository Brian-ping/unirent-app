import os
from flask import Flask
from flask_mail import Mail, Message
from pymongo import MongoClient
from apscheduler.schedulers.background import BackgroundScheduler

# Initialize extensions
mail = Mail()
scheduler = BackgroundScheduler()

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here-change-this-to-something-random')

    # ======================
    # Database Configuration
    # ======================
    client = MongoClient(os.getenv('MONGO_URI', 'mongodb+srv://unirent_app:Chemundu254@cluster0.5f6hd.mongodb.net/Unirent?retryWrites=true&w=majority'))
    db = client['Unirent']
    
    # Attach collections to app
    app.items_collection = db['items']
    app.user_collection = db['users']  # Changed from 'user' to 'users' (recommended)
    app.booking_collection = db['bookings']

    # ======================
    # Email Configuration
    # ======================
    app.config.update(
        MAIL_SERVER='smtp.gmail.com',
        MAIL_PORT=587,
        MAIL_USE_TLS=True,
        MAIL_USERNAME='alexofficial427@gmail.com',  # Your full email
        MAIL_PASSWORD='ffkgneusvxinniaj',  # NEW generated app password
        MAIL_DEFAULT_SENDER=('UniRent', 'alexofficial427@gmail.com')  # Name + email
    )
    mail.init_app(app)

    # ======================
    # Scheduler Setup
    # ======================
    if not scheduler.running:
        scheduler.start()
        
        @app.teardown_appcontext
        def shutdown_scheduler(exception=None):
            if scheduler.running:
                scheduler.shutdown()

    # ======================
    # Routes Registration
    # ======================
    with app.app_context():
        # Test email configuration on startup
        try:
            msg = Message(
                'Application Startup',
                recipients=['recipient@example.com'],  # Use a different email
                body='Email service is working!'
            )
            mail.send(msg)
            app.logger.info("✅ Email service configured successfully")
        except Exception as e:
            app.logger.error(f"❌ Email configuration failed: {str(e)}")

        # Register blueprints
        from app.routes.auth import auth_routes
        from app.routes.main import main_routes
        from app.routes.booking import booking_routes
        
        app.register_blueprint(auth_routes)
        app.register_blueprint(main_routes)
        app.register_blueprint(booking_routes)

    return app