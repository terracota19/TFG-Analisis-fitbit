class Mongo:
    def __init__(self, dbname, mongoClient):
        self.client = mongoClient
        self.db = self.client[dbname]

    def close_connection(self):
        self.client.close()

    # CRUD Operations
    def insert_data(self, collection_name, data):
        collection = self.db[collection_name]
        result = collection.insert_one(data)
        return result.acknowledged

    def find_data(self, collection_name, query):
        collection = self.db[collection_name]
        return collection.find(query)

    def find_one_data(self, collection_name, query):
        collection = self.db[collection_name]
        return collection.find_one(query)
    
    def update_data(self, collection_name, query, field, value):
        collection = self.db[collection_name]
        result = collection.update_one(query, {"$set": {field: value}})
        return result.modified_count

    def delete_data(self, collection_name, query):
        collection = self.db[collection_name]
        result = collection.delete_one(query)
        return result.deleted_count
