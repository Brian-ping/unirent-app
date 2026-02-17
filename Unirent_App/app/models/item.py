from flask import current_app
from bson.objectid import ObjectId

class Item:
    @staticmethod
    def get_collection():
        """Helper method to access the items collection"""
        return current_app.items_collection

    @staticmethod
    def find_by_id(item_id):
        """
        Finds an item by its ID.
        """
        return Item.get_collection().find_one({"_id": ObjectId(item_id)})

    @staticmethod
    def get_all():
        """
        Fetches all items from the database.
        """
        return list(Item.get_collection().find())

    @staticmethod
    def find_by_category(category):
        """
        Finds all items in a specific category.
        """
        return list(Item.get_collection().find({"category": category}))

    @staticmethod
    def find_by_subcategory(subcategory):
        """
        Finds all items in a specific subcategory.
        """
        return list(Item.get_collection().find({"subcategory": subcategory}))

    @staticmethod
    def update_quantity(item_id, quantity):
        """
        Updates the quantity of an item and its availability.
        Returns True if the update was successful, False otherwise.
        """
        try:
            result = Item.get_collection().update_one(
                {"_id": ObjectId(item_id)},
                {"$set": {"quantity": quantity, "availability": quantity > 0}}
            )
            return result.modified_count > 0  # Return True if the item was updated
        except Exception as e:
            print(f"❌ Error updating item quantity: {e}")
            return False  # Return False if an error occurred

    @staticmethod
    def delete(item_id):
        """
        Deletes an item by its ID.
        Returns True if the item was deleted, False otherwise.
        """
        try:
            result = Item.get_collection().delete_one({"_id": ObjectId(item_id)})
            return result.deleted_count > 0  # Return True if the item was deleted
        except Exception as e:
            print(f"❌ Error deleting item: {e}")
            return False  # Return False if an error occurred