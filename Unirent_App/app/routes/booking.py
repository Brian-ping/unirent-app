from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from app.controllers.booking_controller import BookingController
from bson.objectid import ObjectId
from datetime import datetime, timedelta

# Create a Blueprint for booking routes
booking_routes = Blueprint('booking', __name__)

@booking_routes.route('/book/<item_id>', methods=['GET'])
def book_item(item_id):
    """
    Route to display the booking form for a specific item.
    """
    # Check if the user is logged in
    if 'user_id' not in session:
        flash('Please login to continue with your booking.', 'warning')
        # Store the intended booking URL to redirect back after login
        session['next_url'] = url_for('booking.book_item', item_id=item_id)
        return redirect(url_for('auth.login'))

    # Fetch the item details for booking
    item = BookingController.book_item(item_id, session['user_id'])
    if not item:
        flash('Item not found.', 'error')
        return redirect(url_for('main.home'))

    # Render the booking form with the item details
    return render_template('booking_form.html', item=item)

@booking_routes.route('/submit_booking', methods=['POST'])
def submit_booking():
    """
    Route to handle the submission of the booking form.
    """
    # Check if the user is logged in
    if 'user_id' not in session:
        flash('You need to login first.', 'error')
        return redirect(url_for('auth.login'))

    # Get form data
    item_id = request.form['item_id']
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    location = request.form['location']
    start_date = request.form['start_date']

    # Convert start_date to a datetime object
    try:
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        end_date_obj = start_date_obj + timedelta(days=7)  # End date is 7 days later
    except ValueError:
        flash("Invalid date format. Please use YYYY-MM-DD.", "error")
        return redirect(url_for('main.home'))

    # Convert item_id from string to ObjectId
    try:
        item_id_obj = ObjectId(item_id)
    except:
        flash("Invalid item ID", "danger")
        return redirect(url_for('main.home'))

    # Fetch item details from the database
    item = BookingController.find_item_by_id(item_id_obj)
    if not item:
        flash("Item not found.", "danger")
        return redirect(url_for('main.home'))

    # Check if the item is available and quantity > 0
    if not item.get('availability', True) or item.get('quantity', 0) <= 0:
        flash("This item is currently unavailable.", "error")
        return redirect(url_for('main.home'))

    # Initiate payment (STK Push or other payment method)
    amount = item['price']  # Fetch price from the database
    try:
        # Call the payment initiation function
        payment_success = BookingController.initiate_payment(
            phone=phone,
            amount=amount,
            item_id=item_id,
            item_name=item['name']  # Pass the item name for the transaction description
        )
        if payment_success:
            # Save booking details
            booking_details = {
                "item_id": item_id_obj,
                "user_id": session['user_id'],
                "name": name,
                "email": email,
                "phone": phone,
                "location": location,
                "start_date": start_date_obj.strftime('%Y-%m-%d'),
                "end_date": end_date_obj.strftime('%Y-%m-%d'),
                "price": amount,
                "status": "Pending Payment"
            }
            # Save the booking to the database
            booking_id = BookingController.save_booking(booking_details)
            print(f"Booking saved with ID: {booking_id}")  # Log the booking ID

            # Reduce item quantity by 1
            BookingController.update_item_quantity(item_id_obj, item['quantity'] - 1)

            flash("Booking successful! Please complete payment.", "success")
        else:
            flash("Payment initiation failed. Please try again.", "error")
    except Exception as e:
        print(f"❌ Error during booking: {e}")
        flash("An error occurred during booking. Please try again.", "error")

    return redirect(url_for('main.home'))