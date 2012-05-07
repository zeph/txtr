#!/usr/bin/env python
__author__ = 'zeph'
import jsonrpclib, json, pymongo, sys,  time,  threading, xmlrpclib
# this is limiting the number of outgoing connections, not the local threads
# as we have the approach "spawn and forget" ;)
MAX_ACTIVE_THREADS = 30

# hardcoded value on the Reaktor
PAGINATION_LIMIT = 100

jsonrpclib.config.version = 1.0
reaktor = jsonrpclib.Server('http://staging.txtr.com/json/rpc')
token="txtr.it"

try:
    reaktor.WSLookup.getHost()
except xmlrpclib.ProtocolError:
    print >> sys.stderr, " - k, leave it, Reaktor is OFFLINE"
    exit()
except KeyError:
    # http://txtr.com/rest/rpc?service=WSLookup&method=getHost
    print >> sys.stderr, " - k, yes we know. Failing on WSLookup.getHost(), but the Reaktor is there"

mongo_instance = pymongo.Connection('localhost', 27017)
mongodb = mongo_instance.test_reaktor_stg
txtr_it = mongodb["txtr.it"]
# http://www.hacksparrow.com/the-mongodb-tutorial.html
txtr_it.remove() # "truncating" the collection

class ScoutCatalog(threading.Thread):
    def __init__(self,  category_ids = []):
        print >> sys.stderr, ".",
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
            results = reaktor.WSContentCategoryMgmt.getContentCategory(token, c_id, False, None, False, 0, PAGINATION_LIMIT)
            txtr_it.insert(results)
            mongo_instance.end_request()
            if len(results["documentIDs"])!=0:
                thr = ScoutDocuments(results["documentIDs"])
                thr.start()
            if results["size"] > PAGINATION_LIMIT:
                pages = int(results["size"] / PAGINATION_LIMIT)
                for r in xrange(1, pages+1):
                    print (r, pages),
                    subresults = reaktor.WSContentCategoryMgmt.getContentCategory(token, c_id,
                        False, None, False, r*PAGINATION_LIMIT, PAGINATION_LIMIT)
                    if len(subresults["documentIDs"])!=0:
                        thr = ScoutDocuments(results["documentIDs"])
                        thr.start()
            if len(results["childrenIDs"])!=0:
                thr = ScoutCatalog(results["childrenIDs"])
                thr.start()
        pool_thr.release()
        print >> sys.stderr, "\n\t%s secs\t%s " % (round(time.time() - start_time,  2),  [str(x) for x in self.category_ids]),

class ScoutDocuments(threading.Thread):
    def __init__(self, document_ids = []):
        print >> sys.stderr, "x",
        sys.stdout.flush()
        threading.Thread.__init__(self)
        self.document_ids = document_ids
    def run(self):
        pool_thr.acquire()
        start_time = time.time()
        results = reaktor.WSDocMgmt.getDocuments(token, self.document_ids)
        txtr_it.insert(results)
        mongo_instance.end_request()
        pool_thr.release()
        print >> sys.stderr, "\n>\t%s secs\t%s " % (round(time.time() - start_time,  2),  [str(x) for x in self.document_ids]),

# http://stackoverflow.com/questions/42558/python-and-the-singleton-pattern
class Singleton(object):
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            # Semaphore is actually a function, that is why we can't put it as "object" in the Singleton inheritance
            # http://stackoverflow.com/questions/2231427/error-when-calling-the-metaclass-bases-function-argument-1-must-be-code-not
            cls._instance = threading.Semaphore(*args, **kwargs)
        return cls._instance

pool_thr = Singleton(value=MAX_ACTIVE_THREADS)
thr = ScoutCatalog()
thr.start()
thr.join()

print >> sys.stderr, ""
print ""
