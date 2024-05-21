from pymongo import MongoClient

class Mongo:
    def __init__(self, uri, dbname):
        self.client = MongoClient(uri)
        self.db = self.client[dbname]

    def insert_data(self, collection_name, data):
        collection = self.db[collection_name]
        result = collection.insert_one(data)
        return result.inserted_id

    def find_data(self, collection_name, query):
        collection = self.db[collection_name]
        return collection.find(query)

    def update_data(self, collection_name, query, new_values):
        collection = self.db[collection_name]
        result = collection.update_one(query, {"$set": new_values})
        return result.modified_count

    def delete_data(self, collection_name, query):
        collection = self.db[collection_name]
        result = collection.delete_one(query)
        return result.deleted_count

    def close_connection(self):
        self.client.close()
