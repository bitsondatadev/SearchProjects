#!/usr/bin/env python
__author__ = 'brian'
import csv
from itertools import combinations

class SAModel:
	def __init__(self, data, userdata, threshold):
		self.user = {}
		self.userCount = 0
		self.user['locations'] = set()
		self.locations = set()
		self.threshold = float(threshold)
		self.radius = float(.036)
		self.precision = 5 # precision of lat/long. 5 = accuracy of commercial GPS units
		self.N = 0

		userid = userdata[0]['user_id']
		for usertweet in userdata:
			topid = usertweet["label"]
			location = (round(float(usertweet["latitude"]),self.precision), round(float(usertweet["longitude"]),self.precision), usertweet["label"])
			self.user['locations'].add(location)
			
		
		#add all other locations from other users
		for tweet in data:
			if not userid == tweet["user_id"]:
				location = (round(float(tweet["latitude"]),self.precision), round(float(tweet["longitude"]),self.precision), tweet["label"])
				self.locations.add(location)
			self.N += 1

		neighbors = {}
		for i, l1 in enumerate(self.locations):
			for j, l2 in enumerate(self.locations):
				if i < j: #so we don't duplicate our work
					if self.dist(l1, l2, [0,1]) < self.radius:
						if not l1 in neighbors:
							neighbors[l1] = set()
							
						if not l2 in neighbors:
							neighbors[l2] = set()
							
						if not l1 in neighbors[l2]:
							neighbors[l2].add(l1[2])
						
						if not l2 in neighbors[l1]:
							neighbors[l1].add(l2[2])


		self.counts = {}
		#Generate candidates and their counts
		for i in range(1,4):
			for loc in self.locations:
				for n in self.ord_comb(neighbors[loc], i):
					if not n in self.counts:
						self.counts[n] = 0
					self.counts[n] += 1

	def dist(self, instance1, instance2, fields):
		distance = 0
		for f in fields:
			distance += pow((float(instance1[f]) - float(instance2[f])), 2)
		return math.sqrt(distance)
	
	def ord_comb(self,l,n):
		return list(combinations(l,n))
		

	
	def predict(self, location):
		pred = float(0)
		neighbors = []
		for loc in self.user['locations']:
			d = self.dist(location, loc, [0, 1])
			if d < self.radius:
				neighbors.append((loc, d))
		neighbors.sort(key=operator.itemgetter(1))
		labels = set()
		labels.add(location[2])
		for n in neighbors:
			if len(labels) == 2:
				break
			if tuple(labels) in self.counts:
				pred += float(self.counts[tuple(labels)])/self.N
				labels.add(n[0][2])
		return pred
		
		
		
