#!/usr/bin/env python
__author__ = 'brian'
import sys,  numpy as np

def getMovieRating(userId, movieId, data):
	simVec = np.zeros(data["numUsers"])
	nonzeroColumns = np.asarray(np.nonzero(data["trainDat"][userId]))[0]
	for i in range(data["numUsers"]):
		if i == userId:
			simVec[i] = 1.0
		else:
			for j in nonzeroColumns:
				sumi = 0
				sumj = 0
				simVec[i] += (data["trainDat"][i][j] * data["trainDat"][userId][j])
				sumi = data["trainDat"][i][j]
				sumj = data["trainDat"][userId][j]
				den = (np.sqrt(sumi) * np.sqrt(sumj))
				if den == 0:
					simVec[i] = 0
				else:
					simVec[i] /= den
	
	num = 0
	den = 0
	nonzeroRows = np.asarray(np.nonzero(simVec))[0]
	for i in nonzeroRows:
		num += (simVec[i] * (data["trainDat"][i][movieId] - data["meanVec"][i]))
		den += abs(simVec[i])
	return data["meanVec"][userId] + (num / den)

if __name__ == "__main__":
	data = {}
	data["trainDat"] = np.loadtxt("train.txt")
	data["numUsers"] = len(data["trainDat"])
	data["meanVec"] = np.apply_along_axis(lambda row : np.average(row[np.nonzero(row)]), axis = 1, arr=data["trainDat"])
	data["subMeanMat"] = np.copy(data["trainDat"])
	for i in range(data["numUsers"]):
		for j in range(len(data["subMeanMat"][i])):
			data["subMeanMat"][i][j] = data["subMeanMat"][i][j] - data["meanVec"][i]
	print(getMovieRating(int(sys.argv[1]),int(sys.argv[2]), data))
