from flask import Blueprint, render_template, redirect, url_for, flash, session, jsonify
from app.controllers.main_controller import MainController
from app.utils.helper import fetch_and_group_items
from app.models.booking import Booking
from functools import wraps

main_routes = Blueprint('main', __name__)

# Define subcategories for each category - these are the KEYS used in templates
# The helper.py will map these to actual database values
CATEGORY_SUBCATEGORIES = {
    "electronics": ["consoles", "televisions", "cameras_drones", "laptops", "audio_equipments"],
    "real": ["house", "apartments", "land", "storage_units"],
    "transport": ["cars", "motorcycles", "bicycles_scooters", "buses"],
    "events": ["tents", "furnitures", "lighting_decorations", "wedding_grounds"],
    "miscellaneous": ["construction_equipments", "farming_equipments", "books", "musical_equipments"]
}

# Add this context processor to make session available in all templates
@main_routes.app_context_processor
def inject_user():
    return dict(session=session)

@main_routes.route('/')
def home():
    try:
        items = MainController.get_all_items()
        # Ensure items is a list even if None is returned
        if items is None:
            items = []
        # Don't pass session here - it's already available via context processor
        return render_template('main.html', items=items)
    except Exception as e:
        print(f"❌ Error in home route: {e}")
        # Return empty list on error to prevent template crashes
        return render_template('main.html', items=[])

@main_routes.route('/electronics')
def electronics():
    try:
        subcategories = CATEGORY_SUBCATEGORIES.get("electronics", [])
        grouped_items = fetch_and_group_items("electronics", subcategories)
        # Ensure grouped_items is a dictionary
        if grouped_items is None:
            grouped_items = {}
        
        # Debug print
        print(f"📱 Electronics route - Found categories: {list(grouped_items.keys())}")
        
        return render_template('electronics.html', subcategories=grouped_items)
    except Exception as e:
        print(f"❌ Error in electronics route: {e}")
        return render_template('electronics.html', subcategories={})

@main_routes.route('/real')
def real():
    try:
        subcategories = CATEGORY_SUBCATEGORIES.get("real", [])
        grouped_items = fetch_and_group_items("real", subcategories)
        if grouped_items is None:
            grouped_items = {}
        
        # Debug print
        print(f"🏠 Real route - Found categories: {list(grouped_items.keys())}")
        
        return render_template('real.html', subcategories=grouped_items)
    except Exception as e:
        print(f"❌ Error in real route: {e}")
        return render_template('real.html', subcategories={})

@main_routes.route('/transport')
def transport():
    try:
        subcategories = CATEGORY_SUBCATEGORIES.get("transport", [])
        grouped_items = fetch_and_group_items("transport", subcategories)
        if grouped_items is None:
            grouped_items = {}
        
        # Debug print
        print(f"🚗 Transport route - Found categories: {list(grouped_items.keys())}")
        
        return render_template('transport.html', subcategories=grouped_items)
    except Exception as e:
        print(f"❌ Error in transport route: {e}")
        return render_template('transport.html', subcategories={})

@main_routes.route('/events')
def events():
    try:
        subcategories = CATEGORY_SUBCATEGORIES.get("events", [])
        grouped_items = fetch_and_group_items("events", subcategories)
        if grouped_items is None:
            grouped_items = {}
        
        # Debug print
        print(f"🎉 Events route - Found categories: {list(grouped_items.keys())}")
        
        return render_template('events.html', subcategories=grouped_items)
    except Exception as e:
        print(f"❌ Error in events route: {e}")
        return render_template('events.html', subcategories={})

@main_routes.route('/items')
def items():
    try:
        subcategories = CATEGORY_SUBCATEGORIES.get("miscellaneous", [])
        grouped_items = fetch_and_group_items("miscellaneous", subcategories)
        if grouped_items is None:
            grouped_items = {}
        
        # Debug print
        print(f"📦 Items route - Found categories: {list(grouped_items.keys())}")
        
        return render_template('items.html', subcategories=grouped_items)
    except Exception as e:
        print(f"❌ Error in items route: {e}")
        return render_template('items.html', subcategories={})


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:  # Check if user is logged in
            flash('Please login to access this page.', 'warning')
            return redirect(url_for("auth.login"))  # Redirect to login page
        return f(*args, **kwargs)
    return decorated_function


@main_routes.route("/view_bookings")
@login_required
def view_bookings():
    """Route to display ONLY the current user's bookings."""
    try:
        user_id = session.get("user_id")
        if not user_id:
            flash("User not found. Please login again.", "error")
            return redirect(url_for("auth.login"))
            
        bookings = Booking.find_by_user_id(user_id)
        if bookings is None:
            bookings = []
        return render_template("view_bookings.html", bookings=bookings)
    except Exception as e:
        print(f"❌ Error in view_bookings route: {e}")
        flash("Error loading bookings.", "error")
        return render_template("view_bookings.html", bookings=[])


@main_routes.route('/cancel_booking/<booking_id>', methods=['POST'])
def cancel_booking(booking_id):
    """
    Route to cancel a booking.
    """
    try:
        # Update the booking status to "Cancelled"
        Booking.update_status(booking_id, "Cancelled")
        flash("Booking cancelled successfully.", "success")
    except Exception as e:
        print(f"❌ Error cancelling booking: {e}")
        flash("An error occurred while cancelling the booking.", "error")
        
    return redirect(url_for('main.view_bookings'))


# ======================
# DEBUG ROUTE - REMOVE AFTER TESTING
# ======================
@main_routes.route('/debug-db')
def debug_db():
    """Debug route to check database contents"""
    try:
        from flask import current_app
        from bson import json_util
        import json
        
        # Get collection
        collection = current_app.items_collection
        
        # Get all documents
        all_items = list(collection.find({}))
        
        # Convert ObjectId to string for JSON serialization
        for item in all_items:
            item['_id'] = str(item['_id'])
        
        # Get counts by category
        pipeline = [
            {"$group": {"_id": "$category", "count": {"$sum": 1}}}
        ]
        category_counts = list(collection.aggregate(pipeline))
        
        # Get counts by subcategory for each main category
        categories_to_check = ["Electronics", "Vehicle & Transportation", "real", "events", "miscellaneous"]
        subcategory_counts = {}
        
        for cat in categories_to_check:
            pipeline = [
                {"$match": {"category": cat}},
                {"$group": {"_id": "$subcategory", "count": {"$sum": 1}}}
            ]
            subcategory_counts[cat] = list(collection.aggregate(pipeline))
        
        # Get all unique categories
        categories = collection.distinct("category")
        
        return jsonify({
            'total_items': len(all_items),
            'categories': categories,
            'category_counts': category_counts,
            'subcategory_breakdown': subcategory_counts,
            'sample_items': all_items[:3]  # First 3 items as sample
        })
    except Exception as e:
        return jsonify({'error': str(e)})