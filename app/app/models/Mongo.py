class Mongo:
    def __init__(self, dbname, mongoClient):
        """Mongo attributtes"""
        self.client = mongoClient
        self.db = self.client[dbname]
        
    """Close connection with MongoDB"""
    def close_connection(self):
        self.client.close()
        
    """
        Getter of porpuse, FCM and FCR data from user logged.
        
        Parameters:
        -query (str): Query to fetch user data.
    """
    def get_user_porpuse_FCM_FCR(self, query):
        user = self.find_one_data("usuarios", query=query)
        if user:
            return user.get('proposito'), user.get('tanaka'), user.get('FCR')
        else:
            return None, None, None
            
    """
        Stores into mongoDB the restingHeartRate value.
        
        Parameters:
        -user_id (str) : User fitbit id.
        -restingHeartRate (int) : User resting HeartRate from fitbit.
    """
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

    def changeUserPorpouse(self, user_id, new_porpuse):
        return self.update_data("usuarios", query= {"_id" : user_id}, field="proposito", value=new_porpuse)
    
    """
        Changes user secret Password

        Parameters:
        -new_pass (str) : User nee secret password
        -user_id (str) : User Mongo _id
        -salt (str) : Salt generated with SHA-256
    """
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
