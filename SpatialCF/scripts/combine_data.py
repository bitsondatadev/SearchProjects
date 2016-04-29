#!/usr/bin/env python
__author__ = 'brian'
import csv, math, operator

def dist(instance1, instance2, fields):
	distance = 0
	for f in fields:
		distance += pow((float(instance1[f]) - float(instance2[f])), 2)
	return math.sqrt(distance)
	
def getNeighbors(trainingSet, tweet):
	distances = []
	for location in trainingSet:
		distances.append((location, dist(tweet, location, ["latitude", "longitude"])))
	distances.sort(key=operator.itemgetter(1))
	return distances

k = 4
osmlist = list(csv.DictReader(open("..\\data\\osm_tippecanoe_2016.csv", 'r')))
tweetReader = list(csv.DictReader(open("..\\data\\tweet_tippecanoe_2016_1_3.csv", 'r')))
tweetWriter = csv.DictWriter(open("..\\data\\tweet_label_tippecanoe_2016.csv", 'w'), delimiter=',' , lineterminator='\n', fieldnames=['user_id', 'latitude', 'longitude', 'label'])
tweetWriter.writeheader()
for tweet in tweetReader:
	neighbors = getNeighbors(osmlist, tweet)
	lblCnt = {}
	#start out with kNN
	for i in range(k):
		label = neighbors[i][0]["label"]
		if not label in lblCnt:
			lblCnt[label] = 0
		lblCnt[label] += 1
		
	#keep going if more than 1 qualifying label
	i = k
	mval = max(lblCnt.iteritems(), key=operator.itemgetter(1))[1]
	mvals = [key for key in lblCnt.keys() if lblCnt[key] == mval]
	while(len(mvals) > 1):
		label = neighbors[i][0]["label"]
		if not label in lblCnt:
			lblCnt[label] = 0
		lblCnt[label] += 1
		
		mval = max(lblCnt.iteritems(), key=operator.itemgetter(1))[1]
		mvals = [key for key in lblCnt.keys() if lblCnt[key] == mval]
	tweetWriter.writerow({
	'user_id':tweet['user_id'],  
	'latitude':tweet['latitude'], 
	'longitude':tweet['longitude'], 
	'label':mvals[0]
	})