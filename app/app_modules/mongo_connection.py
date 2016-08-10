import pymongo
from pymongo import MongoClient

def connect_client(db_name, collection_name):
    client = MongoClient() #ovako se konektuje na default host i port
    # konekcija sa bilo kojom instancom

    # client = MongoClient('localhost', 27017)
    # client = MongoClient('mongodb://localhost:27017/')

    db = client[db_name]
    #print db
    collection = db[collection_name]
    #print collection
    return db, collection

connect_client('jobs','job-posts')