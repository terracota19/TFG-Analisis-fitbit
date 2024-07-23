class Mongo:
    def __init__(self, dbname, mongoClient):
        
        """Mongo attributtes"""
        self.client = mongoClient
        self.db = self.client[dbname]
        
    """Close connection with MongoDB"""
    def close_connection(self):
        self.client.close()

    def storeRestingHeartRate(self, user_id, restingHeartRate):
        return self.update_data("usuarios", query={"_id": user_id},field="restingHeartRate", value = restingHeartRate)

    """
        Changes logged in user name

        Parameters:
        -new_name (str) : User selected new name.
        -user_id (Object) : User MongoDB Id.
    """
    def changeName(self, new_name, user_id):
        return self.update_data("usuarios", query={"_id":user_id},field="usuario", value=new_name)

    def changePass(self, new_pass, user_id, salt):
        self.update_data("usuarios", query={"_id":user_id}, field="salt", value = salt)
        return self.update_data("usuarios", query={"_id":user_id},field="password", value = new_pass)

    """CRUD Operations"""
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
