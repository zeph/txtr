#!/usr/bin/env python
__author__ = 'zeph'
import jsonrpclib, json, pymongo, sys

jsonrpclib.config.version = 1.0
reaktor = jsonrpclib.Server('http://staging.txtr.com/json/rpc')
token="txtr.it"

mongo_instance = pymongo.Connection('localhost', 27017)
mongodb = mongo_instance.test_reaktor_stg
txtr_it = mongodb["txtr.it"]
# http://www.hacksparrow.com/the-mongodb-tutorial.html
txtr_it.remove() # "truncating" the collection

def scout_catalog(category_ids = [], spacer = " "):
    #print "\nD: %s" % category_ids
    if len(category_ids) == 0:
        results = reaktor.WSContentCategoryMgmt.getCatalogContentCategoryRoots(token)
        #print json.dumps(results, sort_keys=True, indent=4)
        scout_catalog([ el["ID"] for el in results ])
    print "\n"+spacer, 
    for c_id in category_ids: 
        print c_id, 
        sys.stdout.flush() 
        results = reaktor.WSContentCategoryMgmt.getContentCategory(token, c_id, False, None, False, 0, -1)
        txtr_it.insert(results)
        if len(results["childrenIDs"])!=0:
            scout_catalog(results["childrenIDs"],  spacer+" ")
        
scout_catalog() 
print
