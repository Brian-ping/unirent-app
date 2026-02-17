# Unirent_App
 Multicategory items renting 
 # Electronics Product Database

A comprehensive MongoDB database collection containing product information for 12 popular electronics items across multiple categories.

## 📦 Products Included

### Gaming Consoles
- 🎮 PlayStation 5
- 🎮 PlayStation 4

### Televisions
- 📺 TCL Smart TV
- 📺 LG OLED TV

### Drones
- 🚁 DJI Mavic Drone
- 🚁 DJI Mini 2

### Cameras
- 📸 Canon EOS R5
- 📸 GoPro Hero 10

### Laptops
- 💻 Dell XPS 13
- 💻 HP Spectre x360
- 💻 Lenovo ThinkPad X1
- 💻 Asus ROG Zephyrus

## 📊 Database Structure

Each product document contains the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `_id` | ObjectId | Unique identifier (auto-generated) |
| `name` | String | Product name |
| `price` | Int32 | Product price in USD |
| `image_url` | String | URL to product image |
| `category` | String | Main category (electronics) |
| `subcategory` | String | Product subcategory |
| `available_locations` | Array | List of cities where available |
| `availability` | Boolean | In stock status |
| `quantity` | Int32 | Available quantity |
| `description` | String | Product description |

## 🚀 Getting Started

### Prerequisites
- MongoDB installed locally or access to MongoDB Atlas
- MongoDB Compass (optional, for GUI)

### Import the Data

#### Using MongoDB Compass:
1. Open MongoDB Compass
2. Connect to your database (default: `mongodb://localhost:27017`)
3. Create a new database called `electronics_store`
4. Create a new collection called `products`
5. Click "Add Data" → "Import File"
6. Select the `data/products.json` file
7. Click "Import"

#### Using MongoDB Shell:
```bash
mongoimport --db electronics_store --collection products --file data/products.json --jsonArray
