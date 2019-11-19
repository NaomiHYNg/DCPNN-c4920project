from pymongo import MongoClient

class DB():
    
    @staticmethod
    def init():
        mongo_host = "mongodb://admin:admin123@ds331558.mlab.com:31558/comp4920?retryWrites=false"
        mongo_port=27107
        db_name = 'comp4920'

        client = MongoClient(host=mongo_host, port=mongo_port)
        DB.DATABASE = client[db_name]

    @staticmethod
    def insert(collection, data):
        DB.DATABASE[collection].insert(data)
    
    @staticmethod
    def update(collection, query, data):
        DB.DATABASE[collection].update(query, data)

    @staticmethod
    def find_one(collection, query):
        return DB.DATABASE[collection].find_one(query)

    @staticmethod
    def find_all(collection):
        return DB.DATABASE[collection].find()
    
    @staticmethod
    def delete_one(collection, query):
        return DB.DATABASE[collection].delete_one(query)