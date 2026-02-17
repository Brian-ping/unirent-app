from app.models.booking import Booking
from app.models.item import Item
from app.utils.mpesa import initiate_stk_push
from bson.objectid import ObjectId
from datetime import datetime
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class BookingController:
    @staticmethod
    def book_item(item_id, user_id):
        """
        Fetches an item by its ID for booking.
        Returns: item (dict) or None if not found
        """
        try:
            item = Item.find_by_id(item_id)
            if not item:
                logger.warning(f"Item not found: {item_id}")
                return None
            return item
        except Exception as e:
            logger.error(f"Error fetching item {item_id}: {str(e)}")
            return None

    @staticmethod
    def find_item_by_id(item_id):
        """
        Finds an item by its ID.
        Returns: item (dict) or None if not found
        """
        try:
            return Item.find_by_id(item_id)
        except Exception as e:
            logger.error(f"Error finding item {item_id}: {str(e)}")
            return None

    @staticmethod
    def initiate_payment(phone, amount, item_id, item_name):
        """
        Initiates an M-Pesa STK push payment.
        Returns: tuple (success: bool, response: dict)
        """
        try:
            account_reference = f"ITEM_{item_id}"
            transaction_desc = f"Payment for {item_name}"
            
            response = initiate_stk_push(phone, amount, account_reference, transaction_desc)
            if response.get('ResponseCode') == '0':
                logger.info(f"Payment initiated for item {item_id}")
                return True, response
            logger.warning(f"Payment failed for item {item_id}: {response}")
            return False, response
        except Exception as e:
            logger.error(f"Payment error for item {item_id}: {str(e)}")
            return False, {'error': str(e)}

    @staticmethod
    def save_booking(booking_details):
        """
        Saves booking details to the database.
        Returns: tuple (success: bool, booking_id: str/None)
        """
        try:
            # Validate required fields
            required_fields = ['item_id', 'user_id', 'phone', 'price', 
                             'name', 'email', 'location', 'start_date', 'end_date']
            if not all(field in booking_details for field in required_fields):
                raise ValueError("Missing required booking fields")

            booking_id = Booking.create(
                item_id=booking_details["item_id"],
                user_id=booking_details["user_id"],
                phone=booking_details["phone"],
                amount=booking_details["price"],
                name=booking_details["name"],
                email=booking_details["email"],
                location=booking_details["location"],
                start_date=booking_details["start_date"],
                end_date=booking_details["end_date"]
            )
            logger.info(f"Booking created: {booking_id}")
            return True, booking_id
        except Exception as e:
            logger.error(f"Error saving booking: {str(e)}")
            return False, None

    @staticmethod
    def update_item_quantity(item_id, new_quantity):
        """
        Updates the quantity of an item in the database.
        Returns: bool (success status)
        """
        try:
            success = Item.update_quantity(item_id, new_quantity)
            if success:
                logger.info(f"Updated quantity for item {item_id} to {new_quantity}")
            else:
                logger.warning(f"Failed to update quantity for item {item_id}")
            return success
        except Exception as e:
            logger.error(f"Error updating quantity for item {item_id}: {str(e)}")
            return False

    @staticmethod
    def complete_booking_process(item_id, user_id, booking_details):
        """
        Complete booking workflow including payment and inventory update.
        Returns: tuple (success: bool, booking_id: str/None, message: str)
        """
        try:
            # 1. Verify item availability
            item = Item.find_by_id(item_id)
            if not item or item.get('quantity', 0) <= 0:
                return False, None, "Item not available"

            # 2. Initiate payment
            payment_success, payment_response = BookingController.initiate_payment(
                booking_details["phone"],
                booking_details["price"],
                item_id,
                item["name"]
            )
            if not payment_success:
                return False, None, "Payment initiation failed"

            # 3. Create booking record
            booking_success, booking_id = BookingController.save_booking(booking_details)
            if not booking_success:
                return False, None, "Failed to create booking"

            # 4. Update inventory
            new_quantity = item['quantity'] - 1
            if not BookingController.update_item_quantity(item_id, new_quantity):
                logger.warning(f"Inventory update failed for booking {booking_id}")

            return True, booking_id, "Booking completed successfully"
        except Exception as e:
            logger.error(f"Booking process error: {str(e)}")
            return False, None, "Booking process failed"