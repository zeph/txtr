#!/usr/bin/env python
__author__ = 'zeph'
import json, pymongo

mongo_instance = pymongo.Connection('localhost', 27017)
mongodb = mongo_instance.test_reaktor_stg
txtr_it = mongodb["txtr.it"]

print txtr_it.distinct("languageCode")
print txtr_it.find({"javaClass":"com.bookpac.server.document.WSTDocument"}).count()
print len(txtr_it.distinct("attributes.86bd46fb-33b9-44e7-8887-c083d8f73699"))
print len(txtr_it.distinct("documentID"))
print
