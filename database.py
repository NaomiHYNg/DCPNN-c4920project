from pymongo import MongoClient
                    
class DB(object):
    mongo_port = 27107
    mongo_host = "mongodb://admin:admin123@ds331558.mlab.com:31558/comp4920"      
    db_name = 'comp4920'

    @staticmethod
    def init():
        client = MongoClient(host=mongo_host, port=mongo_port)
        DB.DATABASE = client[db_name]                                                                                                                                  
          
    @staticmethod
    def insert(collection, data):
        DB.DATABASE[collection].insert(data)
          
    @staticmethod
    def find_one(collection, query):
        return DB.DATABASE[collection].find_one(query)