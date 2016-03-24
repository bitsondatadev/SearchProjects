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
        rawData = np.loadtxt("train.txt")
        model = int(sys.argv[1]) 
        data = {}
        #data["trainDat"] = rawData[np.ix_(range(10), range(20))]
        data["trainDat"] = rawData

        start = time.clock() 
        ##Train the model
        if model == 2:
            data["meanItemVec"] = np.apply_along_axis(lambda col : np.average(col[np.nonzero(col)]), axis = 0, arr=data["trainDat"])
            execfile("item_based_cfilter.py")
            precomputeSimMatrix(data, 225)
        elif model == 1:
            data["meanVec"] = np.apply_along_axis(lambda row : np.average(row[np.nonzero(row)]), axis = 1, arr=data["trainDat"])
            execfile("mem_based_cfilter.py")
        elif model == 3:
            data["meanVec"] = np.apply_along_axis(lambda row : np.average(row[np.nonzero(row)]), axis = 1, arr=data["trainDat"])
            data["iufVec"] = np.apply_along_axis(lambda col : np.count_nonzero(col), axis = 0, arr=data["trainDat"])
            execfile("iuf_based_cfilter.py")
        

        for training, testing in k_fold_cross_validation(data["trainDat"], K=5):
            ##Run and evaluate the model
            tru = [] 
            pred = [] 
            for i in testing:
                for j in range(len(data["trainDat"][i])):
                    if data["trainDat"][i][j] > 0.0:
                        pred.append(getMovieRating(i, j, data))
                        tru.append(data["trainDat"][i][j])
                    

            print(meanAbsoluteError(tru, pred))

        end = time.clock() 
        print(end - start)
