#!/usr/bin/env python
__author__ = 'brian'
import csv, math, operator

class KTModel:
	def __init__(self, data, userdata, alpha, beta):
		self.user = {}
		self.userCount = 0
		self.user['locations'] = set()
		self.user['topics'] = {}
		self.topics = {}
		self.locations = set()
		self.alpha = float(alpha)
		self.beta = float(beta)
		self.precision = 5 # precision of lat/long. 5 = accuracy of commercial GPS units

		for tweet in userdata:
			topid = tweet["label"]
			location = (round(float(tweet["latitude"]),self.precision), round(float(tweet["longitude"]),self.precision))
			
			self.user['locations'].add(location)

			if not topid in self.user['topics']:
				self.user['topics'][topid] = 0
			self.user['topics'][topid] += 1
		
		userSet = set()
		for tweet in data:
			userSet.add(tweet["user_id"])
			self.locations.add(location)
			
			topid = tweet["label"]
			location = (round(float(tweet["latitude"]),self.precision), round(float(tweet["longitude"]),self.precision))
			if not topid in self.topics:
				self.topics[topid] = {}
			
			if not location in self.topics[topid]:
				self.topics[topid][location] = 0
			self.topics[topid][location] += 1
			
		self.userCount = len(userSet)

	def dist(self, instance1, instance2, fields):
		distance = 0
		for f in fields:
			distance += pow((float(instance1[f]) - float(instance2[f])), 2)
		return math.sqrt(distance)
	
	def predict(self, location):
		topicModelPred = float(0)
		kernelModelPred = float(0)
		
		#calculate topic model
		for top in self.topics:
			if(location in self.topics[top] and top in self.user['topics']):
				topicModelPred += (float(self.topics[top][location]) / len(self.topics)) * (float(self.user['topics'][top]) / self.userCount)
		
		#calcualte kernel model
		for userLocation in self.user['locations']:
			denom = float(0)
			for loc in self.locations:
				denom += math.exp((-self.beta/2) * (self.dist(loc,userLocation,[0,1])**2) )
			kernelModelPred += math.exp((-self.beta/2) * (self.dist(location,userLocation,[0,1])**2) )
			
		kernelModelPred /= denom
		
		return (self.alpha * kernelModelPred) + ((1-self.alpha) * topicModelPred)


