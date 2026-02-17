import os
from pathlib import Path
from dotenv import load_dotenv

# Use absolute path
env_path = Path('C:/Users/kathi/OneDrive/Documents/Unirent App/Unirent_App/.env')
load_dotenv(dotenv_path=env_path, override=True)

MONGO_URI = os.getenv('MONGO_URI')
print(f'Using URI: {MONGO_URI}')

from pymongo import MongoClient
client = MongoClient(MONGO_URI)
client.admin.command('ping')
print('✅ SUCCESS!')
