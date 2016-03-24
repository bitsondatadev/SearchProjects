#!/usr/bin/env python
__author__ = 'brian'
import sys,  numpy as np

def generateSimilarityVec(userId, data):
        if not userId in data["simVec"]:
	    data["simVec"][userId] = np.zeros(len(data["trainDat"]))

	nonzeroColumns = np.asarray(np.nonzero(data["trainDat"][userId]))[0]
	for i in range(len(data["trainDat"])):
		if i != userId:
			sumi = 0
			sumj = 0
			for j in nonzeroColumns:
				data["simVec"][userId][i] += (data["trainDat"][i][j] * data["trainDat"][userId][j])
				sumi += pow(data["trainDat"][i][j], 2)
				sumj += pow(data["trainDat"][userId][j], 2)

			den = (np.sqrt(sumi) * np.sqrt(sumj))
			if den != 0:
				data["simVec"][userId][i] /= den
	

def getMovieRating(userId, movieId, data):
        if not "simVec" in data:
            data["simVec"] = {}
        generateSimilarityVec(userId, data)
	num = 0
	den = 0
	nonzeroRows = np.asarray(np.nonzero(data["simVec"][userId]))[0]
	for i in nonzeroRows:
		if data["trainDat"][i][movieId] != 0:
		    num += (data["simVec"][userId][i] * (data["trainDat"][i][movieId] - data["meanVec"][i]))
		    den += abs(data["simVec"][userId][i])
	return data["meanVec"][userId] + ((num / den) if den > 0 else 0)

