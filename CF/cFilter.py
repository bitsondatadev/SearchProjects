#!/usr/bin/env python
__author__ = 'brian'
import sys,  numpy as np

def getMovieRating(userId, movieId):
	simVec = np.zeros(numUsers)
	for i in range(numUsers):
 		if i == userId:
	 		simVec[i] = 1.0
 		else:
	 		sumi = 0
	 		sumj = 0
	 		simVec[i] = (simVec[i] + (trainDat[i][movieId] * trainDat[userId][movieId])) * 1.0
	 		sumi = trainDat[i][movieId]
	 		sumj = trainDat[userId][movieId]

		den = (np.sqrt(sumi) * np.sqrt(sumj))

		if den == 0:
			simVec[i] = 0
		else:
			simVec[i] = (simVec[i] / den)
	
	num = 0
	den = 0
	for i in range(numUsers):
		num = num + (simVec[i] * (trainDat[i][movieId] - meanVec[i]))
		den = simVec[i];
	print(simVec)
	return meanVec[userId] + (num / den)

if __name__ == "__main__":
	trainDat = np.loadtxt("train.txt")
	numUsers = len(trainDat)
	meanVec = np.apply_along_axis(lambda row : np.average(row[np.nonzero(row)]), axis = 1, arr=trainDat)
	subMeanMat = np.copy(trainDat)
	
	for i in range(numUsers):
		for j in range(len(subMeanMat[i])):
			subMeanMat[i][j] = subMeanMat[i][j] - meanVec[i]

	similarityMatrix = np.zeros(shape = (numUsers,numUsers) )

	
	getMovieRating(2, 1)
