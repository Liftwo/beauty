import pymongo

client = pymongo.MongoClient('18.141.69.164', 10002)
db = client.hinh
db.authenticate('andy', 'andy')
data = db.drfworks_works.find({'platform':'tw'})
for x in data:
    print(x)
# for x in data:
#     if x['platform'] == "tw":
#         link = x['urlLink']
#         number = link.split('/')[-1]
#         print(number)
#
#         db.drfworks_works.update_one({'_id': x['_id']}, {"$set": {"embed": str(number)}}, upsert=True)
#     else:
#         db.drfworks_works.update_one({'_id': x['_id']}, {"$set": {"embed": ""}}, upsert=True)