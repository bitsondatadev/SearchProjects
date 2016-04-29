#!/usr/bin/env python
__author__ = 'brian'
import sys, csv,  numpy as np
import time 
from sklearn.metrics import mean_squared_error

def k_fold_cross_validation(X, K):
	""" 
	Generates K (training, validation) pairs from the items in X.
        Source: http://code.activestate.com/recipes/521906-k-fold-cross-validation-partition/
	"""
	for k in xrange(K):
		training = [i for i, x in enumerate(X) if i % K != k]
		validation = [i for i, x in enumerate(X) if i % K == k]
		yield training, validation



if __name__ == "__main__":
	model = int(sys.argv[1]) 
	execfile("kernel_topic_model.py")
	
	user_ids = [
	#'17322758', #1311
	#'252620329', #433
	'388997369', #110
	'2350966291', #103
	'44524722', #66
	'55862979', #58
	'48134589', #55
	'205530091', #55
	'1925340810', #45
	'20168184', #45
	'22896762', #42
	'136798620', #42
	#'4681825992', #40
	#'122111322', #40
	#'83695067' #38
	]
	tweetReader = list(csv.DictReader(open("..\\data\\tweet_label_tippecanoe_2016.csv", 'r')))
	users = {}
	
	for tweet in tweetReader:
		uid = tweet["user_id"]
		if not uid in users:
			users[uid] = []
			
		users[uid].append(tweet)
		
	print "Num Users: " + str(len(users))
	
	start = time.clock() 
	##Train the model
	if model == 1:
		alpha = .25
		beta = 100
		resultsWriter = csv.DictWriter(open("..\\analysis\\kernel_topic_mse.csv", 'w'), delimiter=',' , lineterminator='\n', fieldnames=['user_id', 'MSE'])
		resultsWriter.writeheader()
		for i, user in enumerate(user_ids):
			print "Evaluating for user: " + user + " Completed: %" + str(float(i)/len(user_ids) * 100)
			
			avgMSE = 0
			for training, testing in k_fold_cross_validation(users[user], K=5):
				##Run and evaluate the model
				trainDat = [users[user][i] for i in training]
				kt = KTModel(tweetReader, trainDat, alpha, beta)
				tru = [] 
				pred = [] 
				for i in testing:
					tweet = users[user][i]
					location = (round(float(tweet["latitude"]),kt.precision), round(float(tweet["longitude"]),kt.precision))
					pred.append(kt.predict(location))
					tru.append(1)
				avgMSE += mean_squared_error(tru, pred)
			resultsWriter.writerow({'user_id':user, 'MSE':avgMSE / 5})
    #    elif model == 2:
	end = time.clock() 
	print(end - start)
