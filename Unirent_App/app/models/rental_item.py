import random
from flask import current_app

class RentalItem:
    
    CATEGORIES = {
        "electronics": ["consoles", "televisions", "cameras_drones", "laptops", "audio_equipments"],
        "real": ["house", "apartments", "land", "storage_units"],
        "transport": ["cars", "motorcycles", "bicycles_scooters", "buses"],
        "events": ["tents", "furnitures", "lighting_decorations", "wedding_grounds"],
        "miscellaneous": ["construction_equipments", "farming_equipments", "books", "musical_equipments"]
    }

    @classmethod
    def get_featured_items(cls, count=6, use_db=True):
        """Get featured items from database with fallback to mock data"""
        try:
            if use_db and hasattr(current_app, 'extensions') and 'mongo' in current_app.extensions:
                return cls._get_from_database(count)
            return cls._generate_mock_items(count)
        except Exception as e:
            current_app.logger.error(f"Error getting featured items: {str(e)}")
            return cls._generate_mock_items(count)

    @classmethod
    def _get_from_database(cls, count):
        """Get random items from MongoDB with their actual image URLs"""
        pipeline = [
            {'$match': {'is_featured': True}},
            {'$sample': {'size': count}},
            {'$project': {
                '_id': {'$toString': '$_id'},
                'name': 1,
                'category': 1,
                'subcategory': 1,
                'price': 1,
                'image_url': 1,  # Using the actual image URL from database
                'available_locations': 1,
                'quantity': 1,
                'availability': {'$gt': ['$quantity', 0]}
            }}
        ]
        
        items = list(current_app.mongo.db.items.aggregate(pipeline))
        
        # Ensure all items have required fields
        for item in items:
            item.setdefault('image_url', cls._get_fallback_image_url(item.get('category')))
        
        return items

    @classmethod
    def _generate_mock_items(cls, count):
        """Generate mock items with placeholder images"""
        current_app.logger.debug("Generating mock featured items")
        return [cls._create_mock_item() for _ in range(count)]

    @classmethod
    def _create_mock_item(cls):
        """Create a single mock rental item with placeholder image"""
        category = random.choice(list(cls.CATEGORIES.keys()))
        subcategory = random.choice(cls.CATEGORIES[category])
        
        return {
            '_id': str(random.randint(1000, 9999)),
            'name': f"Premium {subcategory.replace('_', ' ').title()}",
            'category': category.title(),
            'subcategory': subcategory.replace('_', ' ').title(),
            'price': random.randint(500, 5000),
            'image_url': cls._get_fallback_image_url(category),
            'available_locations': random.sample(
                ["Nairobi", "Mombasa", "Kisumu", "Nakuru", "Eldoret"], 
                random.randint(1, 3)
            ),
            'availability': random.choice([True, False]),
            'quantity': random.randint(0, 10)
        }

    @staticmethod
    def _get_fallback_image_url(category):
        """Get a fallback image URL if none exists in database"""
        category = (category or '').lower()
        fallback_images = {
            "electronics": "https://example.com/fallbacks/electronics.jpg",
            "real": "https://example.com/fallbacks/realestate.jpg",
            "transport": "https://example.com/fallbacks/transport.jpg",
            "events": "https://example.com/fallbacks/events.jpg",
            "miscellaneous": "https://example.com/fallbacks/misc.jpg"
        }
        return fallback_images.get(category, "https://example.com/fallbacks/default.jpg")