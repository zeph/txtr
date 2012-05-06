#!/usr/bin/env python
__author__ = 'zeph'
import jsonrpclib, json, pymongo

jsonrpclib.config.version = 1.0
reaktor = jsonrpclib.Server('http://staging.txtr.com/json/rpc')

results = reaktor.WSAuth.authenticateAnonymousUser("txtr.it")
token = results["token"]
print token

mongo_instance = pymongo.Connection('localhost', 27017)
mongodb = mongo_instance.test_reaktor_stg
txtr_it = mongodb["txtr.it"]
# http://www.hacksparrow.com/the-mongodb-tutorial.html
txtr_it.remove() # "truncating" the collection

results = reaktor.WSContentCategoryMgmt.getCatalogContentCategoryRoots(token)
#print json.dumps(results, sort_keys=True, indent=4)
category_ids = [ el["ID"] for el in results ]

txtr_it.insert(results)

for c_id in category_ids:
    print c_id
    subresults = reaktor.WSContentCategoryMgmt.getContentCategory(token, c_id, False, None, False, 0, -1)
    txtr_it.insert(subresults)
    #print json.dumps(subresults, sort_keys=True, indent=4)
    #print ("CAT", subresults["childrenIDs"])
    #print subresults["documentIDs"]

#for cat in txtr_it.find():
#    print cat

