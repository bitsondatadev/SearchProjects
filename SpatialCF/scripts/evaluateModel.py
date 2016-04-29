#!/usr/bin/env python
__author__ = 'brian'
import sys,  numpy as np
import time 

def k_fold_cross_validation(X, K):
	""" 
	Generates K (training, validation) pairs from the items in X.
        Source: http://code.activestate.com/recipes/521906-k-fold-cross-validation-partition/
	"""
	for k in xrange(K):
		training = [i for i, x in enumerate(X) if i % K != k]
		validation = [i for i, x in enumerate(X) if i % K == k]
		yield training, validation

def meanAbsoluteError(train, test):
    N = len(train)
    num = 0
    for i in range(N):
        num += abs(train[i] - test[i])

    return num/N if N > 0 and N == len(test) else -1

if __name__ == "__main__":
        model = int(sys.argv[1]) 
        execfile("kernel_topic_model.py")

        start = time.clock() 
        ##Train the model
        if model == 1:
            kt = KTModel()
            for user in kt.users:
                for loc in kt.locations:
                    print "User: " + user + " Location: (" + str(loc[0]) + ", " + str(loc[1]) + ") Probability: " + str(kt.predict(loc, user))
#        elif model == 2:


        for training, testing in k_fold_cross_validation(data["trainDat"], K=5):
            ##Run and evaluate the model
            tru = [] 
            pred = [] 
            for i in testing:
                for j in range(len(data["trainDat"][i])):
                    if data["trainDat"][i][j] > 0.0:
                        pred.append(getMovieRating(i, j, data))
                        tru.append(data["trainDat"][i][j])
                    

#            print(meanAbsoluteError(tru, pred))
        end = time.clock() 
        print(end - start)
