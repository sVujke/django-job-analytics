import mongo_connection
import pprint
from bson.son import SON

db, collection = mongo_connection.connect_client('jobs_db','job_posts')

query_set = collection.find()

query_set_size = query_set.count()

print query_set_size

# printing one docuent
one = collection.find_one()
pprint.pprint(one)

# printing the number of documents with city: Beograd and Belgrade
def count_by_key(key, value):
    return collection.find({key:value}).count()
beograd = collection.find({"city":"Beograd"}).count()
# print "Oglasi iz Beograda"
# pprint.pprint(beograd)

belgrade = collection.find({"city":"Belgrade"}).count()
# print "Oglasi iz Belgrade"
# pprint.pprint(belgrade)

belgrade = collection.find({"city":{ '$in': ["Belgrade", "Beograd"]}}).count()
# print "Oglasi iz Belgrade i Beograd"
# pprint.pprint(belgrade)

# printing number of jobs with java tag query for list
java = collection.find({"tags":"java"}).count()
# print "Oglasi sa tagom Java:"
# pprint.pprint(java)

# unique values for companies
unique = collection.distinct("firm")
#for firm in unique:
#    pprint.pprint(firm)
# print "No. of companies that advertise positions"
# print len(unique)
# print unique

unique = collection.distinct("tags")
#for firm in unique:
#    pprint.pprint(firm)
# print "No. of unique tags"
# print len(unique)
# print unique

#https://api.mongodb.com/python/current/examples/aggregation.html


pipeline = [
    {"$unwind": "$tags"},
    {"$group": {"_id": "$tags", "count": {"$sum": 1}}},
     {"$sort": SON([("count", -1), ("_id", -1)])}
 ]
#list(db.things.aggregate(pipeline))

print "Frekvencijski recnik"
print list(collection.aggregate(pipeline))


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

# print "Frekvencijski recnik"
# print list(collection.aggregate

count_by_key("city","Belgrade")