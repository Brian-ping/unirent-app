# app/utils/helper.py
from flask import current_app

def fetch_and_group_items(category_key, subcategories):
    """
    Fetch items from database and group them by subcategory.
    Handles different naming conventions between code and database.
    """
    try:
        # Access collection through current_app
        items_collection = current_app.items_collection
        
        # Map UI category names to database category names
        category_map = {
            # Transport
            "transport": "Vehicle & Transportation",
            
            # Electronics - your DB has both "Electronics" and "electronics"
            "electronics": "Electronics",  
            
            # Real Estate
            "real": "real",
            
            # Events
            "events": "events",
            
            # Miscellaneous
            "miscellaneous": "miscellaneous"
        }
        
        # Get the actual database category name
        db_category = category_map.get(category_key, category_key)
        
        print(f"🔍 Fetching items for category key: '{category_key}' -> DB category: '{db_category}'")
        
        # Get all items for this category
        all_items = list(items_collection.find({"category": db_category}))
        print(f"📊 Found {len(all_items)} items for category '{db_category}'")
        
        # Define mapping for subcategory name variations
        subcategory_map = {
            # Transport mappings
            "cars": ["Cars", "car", "cars"],
            "motorcycles": ["Motorcycles", "motorcycle", "bikes"],
            "bicycles_scooters": ["Bicycles & Scooters", "bicycles", "scooters"],
            "buses": ["Buses", "bus"],
            
            # Real Estate mappings
            "house": ["house", "houses", "House", "Houses"],
            "apartments": ["apartments", "Apartment", "Apartments", "flat"],
            "land": ["land", "Land", "plots"],
            "storage_units": ["storage_units", "storage", "Storage Units"],
            
            # Electronics mappings
            "consoles": ["consoles", "Consoles", "gaming"],
            "televisions": ["televisions", "TVs", "Televisions", "tv"],
            "cameras_drones": ["cameras_drones", "Cameras", "Drones"],
            "laptops": ["laptops", "Laptops", "notebook"],
            "audio_equipments": ["audio_equipments", "Audio", "speakers"],
            
            # Events mappings
            "tents": ["tents", "Tents", "tent"],
            "furnitures": ["furnitures", "Furniture", "furniture"],
            "lighting_decorations": ["lighting_decorations", "Lighting", "decorations"],
            "wedding_grounds": ["wedding_grounds", "Wedding Grounds", "venue"],
            
            # Miscellaneous mappings
            "construction_equipments": ["construction_equipments", "Construction", "tools"],
            "farming_equipments": ["farming_equipments", "Farming", "agricultural"],
            "books": ["books", "Books", "book"],
            "musical_equipments": ["musical_equipments", "Musical", "instruments"]
        }
        
        # Group items by subcategory
        grouped_items = {}
        
        for item in all_items:
            db_subcategory = item.get('subcategory', '')
            
            # Try to match with our expected subcategory keys
            matched_key = None
            for subcat_key in subcategories:
                # Get possible variations for this subcategory
                variations = subcategory_map.get(subcat_key, [subcat_key])
                
                # Check if db_subcategory matches any variation
                if db_subcategory in variations or db_subcategory.lower() in [v.lower() for v in variations]:
                    matched_key = subcat_key
                    break
            
            if matched_key:
                if matched_key not in grouped_items:
                    grouped_items[matched_key] = []
                grouped_items[matched_key].append(item)
            else:
                print(f"⚠️ No match for subcategory: '{db_subcategory}'")
        
        # Debug print
        for key, items in grouped_items.items():
            print(f"✅ {key}: {len(items)} items")
        
        return grouped_items
        
    except Exception as e:
        print(f"❌ Error fetching items: {str(e)}")
        return {}