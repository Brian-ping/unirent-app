import os
from dotenv import load_dotenv
from pymongo import MongoClient

# Load .env file
load_dotenv()
MONGO_URI = os.getenv('MONGO_URI')

print(f"Using URI: {MONGO_URI}")

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    print('✅ SUCCESS! Connected to MongoDB Atlas!')
    
    db = client['Unirent']
    print(f'✅ Collections: {db.list_collection_names()}')
except Exception as e:
    print(f'❌ Connection failed: {e}')
