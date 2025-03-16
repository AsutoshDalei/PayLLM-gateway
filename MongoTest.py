from pymongo import MongoClient
import json

# MongoDB Configuration
MONGO_URI = "mongodb://localhost:27017/"  # Change if using MongoDB Atlas
MONGO_DB = "bbps"
MONGO_COLLECTION = "bbps_categories_details"

# Connect to MongoDB
try:
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    biller_collection = db[MONGO_COLLECTION]

    # Ping MongoDB to verify connection
    db.command("ping")
    print("✅ Connected to MongoDB successfully!")

    # Fetch only billers related to "Electricity"
    electricity_billers = list(biller_collection.find({"category_name": "Electricity"}, {"_id": 0}))

    if electricity_billers:
        print("🔹 Electricity Billers Found:")
        print(json.dumps(electricity_billers, indent=4))  # Pretty print JSON data
    else:
        print("❌ No Electricity billers found in the database.")

except Exception as e:
    print("❌ MongoDB Connection Failed:", e)
