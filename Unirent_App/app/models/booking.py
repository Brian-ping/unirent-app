# app/models/booking.py
from flask import current_app
from bson.objectid import ObjectId
from datetime import datetime


class Booking:

    @staticmethod
    def get_collection():
        """Access the booking collection through current_app"""
        return current_app.booking_collection

    @staticmethod
    def create(item_id, user_id, phone, amount, name, email, location, start_date, end_date):
        """
        Creates a new booking record and automatically fetches item name.
        """
        from app.models.item import Item  # Import at method level to avoid circular imports
        
        # Fetch item details from database
        item = Item.find_by_id(item_id)
        if not item:
            raise ValueError(f"Item with ID {item_id} not found")

        booking_data = {
            "item_id": ObjectId(item_id),
            "item_name": item.get('name'),  # Get name from the item document
            "user_id": ObjectId(user_id),
            "phone": phone,
            "amount": float(amount),
            "name": name,
            "email": email,
            "location": location,
            "start_date": datetime.strptime(start_date, "%Y-%m-%d"),
            "end_date": datetime.strptime(end_date, "%Y-%m-%d"),
            "status": "Pending",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = Booking.get_collection().insert_one(booking_data)
        return str(result.inserted_id)

    @staticmethod
    def find_by_id(booking_id):
        """Finds a booking by its ID"""
        return Booking.get_collection().find_one({"_id": ObjectId(booking_id)})

    @staticmethod
    def update_status(booking_id, status):
        """Updates booking status"""
        Booking.get_collection().update_one(
            {"_id": ObjectId(booking_id)},
            {"$set": {
                "status": status,
                "updated_at": datetime.now()
            }}
        )

    @staticmethod
    def delete(booking_id):
        """Deletes a booking"""
        Booking.get_collection().delete_one({"_id": ObjectId(booking_id)})

    @staticmethod
    def find_all():
        """Gets all bookings"""
        return list(Booking.get_collection().find())

    @staticmethod
    def find_by_user_id(user_id):
        try:
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)

            pipeline = [
                {"$match": {"user_id": user_id}},
                {"$lookup": {
                    "from": "items",
                    "localField": "item_id",
                    "foreignField": "_id",
                    "as": "item_details"
                }},
                {"$unwind": {
                    "path": "$item_details",
                    "preserveNullAndEmptyArrays": True
                }},
                {"$addFields": {
                    "item_name": "$item_details.name",
                    "item_image": "$item_details.image_url",
                    "item_price": "$item_details.price",
                    "item_category": "$item_details.category"
                }},
                {"$project": {
                    "_id": 1,
                    "item_id": 1,
                    "user_id": 1,
                    "item_name": 1,
                    "item_image": 1,
                    "item_price": 1,
                    "item_category": 1,
                    "start_date": 1,
                    "end_date": 1,
                    "status": 1,
                    "created_at": 1,
                    "amount": 1,
                    "phone": 1,
                    "name": 1,
                    "email": 1,
                    "location": 1
                }},
                {"$sort": {"created_at": -1}}
            ]
            
            bookings = list(Booking.get_collection().aggregate(pipeline))
            
            # Convert ObjectIds to strings and format dates
            for booking in bookings:
                booking['_id'] = str(booking['_id'])
                booking['item_id'] = str(booking.get('item_id', ''))
                booking['user_id'] = str(booking.get('user_id', ''))
                if 'start_date' in booking:
                    booking['start_date'] = booking['start_date'].strftime('%Y-%m-%d')
                if 'end_date' in booking:
                    booking['end_date'] = booking['end_date'].strftime('%Y-%m-%d')
                if 'created_at' in booking:
                    booking['created_at'] = booking['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            
            return bookings
            
        except Exception as e:
            print(f"❌ Error finding bookings for user {user_id}: {str(e)}")
            return []