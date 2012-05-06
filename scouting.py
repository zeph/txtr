#!/usr/bin/env python
__author__ = 'zeph'
import jsonrpclib, json, pymongo, sys,  time,  threading

# FIXME / TODO 
# very limited value, cause the locking mechanism seems not to be handled by a singleton
maxthreads = 3

jsonrpclib.config.version = 1.0
reaktor = jsonrpclib.Server('http://staging.txtr.com/json/rpc')
token="txtr.it"

mongo_instance = pymongo.Connection('localhost', 27017)
mongodb = mongo_instance.test_reaktor_stg
txtr_it = mongodb["txtr.it"]
# http://www.hacksparrow.com/the-mongodb-tutorial.html
txtr_it.remove() # "truncating" the collection

class ScoutCatalog(threading.Thread):
    def __init__(self,  category_ids = []):
        print ".", 
        sys.stdout.flush()
        threading.Thread.__init__(self)
        self.category_ids = category_ids
    def run(self):
        pool_thr.acquire()
        start_time = time.time()
        if len(self.category_ids) == 0:
            results = reaktor.WSContentCategoryMgmt.getCatalogContentCategoryRoots(token)
            #print json.dumps(results, sort_keys=True, indent=4)
            thr = ScoutCatalog([ el["ID"] for el in results ])
            thr.start()
        for c_id in self.category_ids: 
            results = reaktor.WSContentCategoryMgmt.getContentCategory(token, c_id, False, None, False, 0, -1)
            txtr_it.insert(results)
            if len(results["childrenIDs"])!=0:
                thr = ScoutCatalog(results["childrenIDs"])
                thr.start()
        pool_thr.release()
        print "\n\t%s secs\t%s " % (round(time.time() - start_time,  2),  [str(x) for x in self.category_ids]), 
        
pool_thr = threading.BoundedSemaphore(value=maxthreads)
thr = ScoutCatalog() 
thr.start()
thr.join()
print
