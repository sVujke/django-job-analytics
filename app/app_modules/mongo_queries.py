import mongo_connection
import pprint
from bson.son import SON
import pymongo

db, collection = mongo_connection.connect_client('jobs_db','job_ads')

query_set = collection.find()

query_set_size = query_set.count()


# printing the number of documents with city: Beograd and Belgrade
def count_by_key(key, value):
    return collection.find({key:value}).count()


def timeline_for_key(key,value):
    dkey = "$"+key
    pipeline = [
    {"$unwind": dkey},
    {"$match": { key: value}},
    {"$group": {"_id": "$date", "count": {"$sum": 1}}},
    {"$sort": {"_id": 1}}
    ]
    return list(collection.aggregate(pipeline))

def rimeline_for_all():

    pipeline = [
    {"$group": {"_id": "$date", "count": {"$sum": 1}}},
    {"$sort": {"_id": 1}}
    ]

    return list(collection.aggregate(pipeline))

#https://api.mongodb.com/python/current/examples/aggregation.html


pipeline = [
    {"$unwind": "$tags"},
    {"$group": {"_id": "$tags", "count": {"$sum": 1}}},
     {"$sort": SON([("count", -1), ("_id", -1)])}
 ]
#list(db.things.aggregate(pipeline))




pipeline = [
    {"$unwind": "$city"},
    {"$group": {"_id": "$city", "count": {"$sum": 1}}},
     {"$sort": SON([("count", -1), ("_id", -1)])}
 ]

def top_x(x,key1,value,dkey):

    pipeline = [
    {"$match": {key1: value}},
    {"$unwind": dkey},
    {"$group": {"_id": dkey, "count": {"$sum": 1}}},
    {"$sort": SON([("count", -1), ("_id", -1)])}
    ]
    return list(collection.aggregate(pipeline))[:x]



def unique(key):
    return collection.distinct(key)


