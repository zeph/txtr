#!/usr/bin/env python
__author__ = 'zeph'
import json, pymongo

mongo_instance = pymongo.Connection('localhost', 27017)
mongodb = mongo_instance.test_reaktor_stg
txtr_it = mongodb["txtr.it"]

print txtr_it.find().count()