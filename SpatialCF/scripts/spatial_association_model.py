#!/usr/bin/env python
__author__ = 'brian'
import csv

class SAModel:
	def __init__(self):
		self.users = {}
		self.topics = {}
		self.locations = set()
		self.N = 0
		self.precision = 5 # accuracy of commercial GPS units
		
		tweetReader = list(csv.DictReader(open("..\\data\\tweet_label_tippecanoe_2016.csv", 'r')))
		self.N = len(tweetReader)
		for tweet in tweetReader:
			uid = tweet["user_id"]
			topid = tweet["label"]
			location = (round(float(tweet["latitude"]),self.precision), round(float(tweet["longitude"]),self.precision))
			
			if not uid in self.users:
				self.users[uid] = {}
				
			self.locations.add(location)
			
			if not topid in self.users[uid]:
				self.users[uid][topid] = 0
			self.users[uid][topid] += 1
			
			if not topid in self.topics:
				self.topics[topid] = {}
				
			if not location in self.topics[topid]:
				self.topics[topid][location] = 0
			self.topics[topid][location] += 1


		print "Num Users: " + str(len(self.users.keys()))
		print "Num Topics: " + str(len(self.topics.keys()))
		print "Num Locations: " + str(len(self.locations))

	
	def predict(self, location, user):
		sum = float(0)
		for top in self.topics:
			if(location in self.topics[top] and top in self.users[user]):
				sum += float(float(self.topics[top][location] / len(self.topics)) * float(self.users[user][top] / len(self.users)))

		return sum

