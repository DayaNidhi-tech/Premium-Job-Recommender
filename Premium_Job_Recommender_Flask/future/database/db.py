from pymongo import MongoClient

# Connect to local MongoDB
client = MongoClient("mongodb://localhost:27017")

# Create / use database
db = client["jobpilot_pro"]

# Collections
applications_col = db["applications"]