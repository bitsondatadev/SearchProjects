#!/usr/bin/env python
__author__ = 'brian'
import csv

tweetReader = list(csv.DictReader(open("..\\data\\tweet_label_tippecanoe_2016.csv", 'r')))
users = {}
for tweet in tweetReader:
	uid = tweet["user_id"]
	if not uid in users:
		users[uid] = []
	users[uid].append(tweet)

numUsers = len(users.keys())
print numUsers
