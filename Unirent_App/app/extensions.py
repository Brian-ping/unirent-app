from flask_mail import Mail
from apscheduler.schedulers.background import BackgroundScheduler
from pymongo import MongoClient

mail = Mail()
scheduler = BackgroundScheduler()
mongo_client = MongoClient()