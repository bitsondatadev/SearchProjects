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
bot_ids = [
'127715541', #weather bot
'100047198', #job bot
'99334945', #job bot
'120669047', #job bot
'3417954461', #job bot
'149017831', #job bot
'1068989126', #job bot
'39155618', #job bot
'220254376', #job bot
'71970659', #job bot
'72653327', #job bot
'22494365', #job bot
'3144822634', #job bot
'150474455', #job bot
'23610727', #ad bot
'357112213', #job bot
'29604233', #job bot
'336113098', #job bot
'120347982', #job bot
'113473032', #job bot
'286248077', #job bot
'21725584', #job bot
'171952691', #job bot
'181424554', #job bot
'28542508', #job bot
'2654767718', #job bot
'2362771358', #job bot
'21837028', #job bot
'236698878', #job bot
'563319506', #job bot
'395561058', #job bot
'3290111838', #job bot
'907218679', #location bot
'2535717440', #job bot
'2904664975' #job bot
]

for tweet in tweetReader:
	if not tweet['user_id'] in bot_ids:
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