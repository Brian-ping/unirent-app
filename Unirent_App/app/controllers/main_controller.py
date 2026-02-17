# app/controllers/main_controller.py
from flask import current_app

class MainController:
    @staticmethod
    def get_all_items():
        try:
            # Access through current_app
            return list(current_app.items_collection.find())
        except Exception as e:
            print(f"❌ Error getting all items: {str(e)}")
            return []