from sqlalchemy import text
from pymongo import MongoClient

client_mongodb = MongoClient('mongodb://127.0.0.1:27017/')
db_mongodb = client_mongodb['bookstore']
mongodb = db_mongodb['book']

count = mongodb.count_documents({"$text": {"$search": "哭泣"}})
print(count)