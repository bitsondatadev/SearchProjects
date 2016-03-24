#!/usr/bin/env python
__author__ = 'brian'
import sys,  numpy as np

def getMovieRating(userId, movieId, data):
	num = 0
	den = 0
	for (simVal, itemIndex) in data["simMatrix"][movieId]:
            if(simVal != 0 and itemIndex > 0):
                userRating = data["trainDat"][userId][int(itemIndex)]
                num += (simVal * userRating)
                den += abs(simVal)

        prediction = (num / den) if den > 0 else 0.0
        prediction =  5.0 if prediction > 5.0 else prediction
	return prediction

def precomputeSimMatrix(data, k):
        m = len(data["trainDat"])
        n = len(data["trainDat"][0])
        data["simMatrix"] = np.array([[(0.0,-999)] * k] * n) #np.zeros((n, k))
        for i in range(n):
           for j in range(i + 1,n):
                num = 0
                sumi = 0
                sumj = 0
                for u in range(m):
                    if data["trainDat"][u][i] != 0 and data["trainDat"][u][j] != 0:
                        smeani = data["trainDat"][u][i] - data["meanItemVec"][i]
                        smeanj = data["trainDat"][u][j] - data["meanItemVec"][j]
                        num += smeani * smeanj
                        sumi += pow(smeani,2) 
                        sumj += pow(smeanj,2) 

                den = np.sqrt(sumi) * np.sqrt(sumj) 
                simij = 0.0 if den == 0 else num / den
                iTup = (simij,j)
                jTup = (simij,i)
                for l in range(k):
                    if(iTup[0] > data["simMatrix"][i][l][0]):
                        (sim, idx) = data["simMatrix"][i][l] 
                        data["simMatrix"][i][l] = iTup
                        iTup = (sim, idx)
                        l = k 

                for l in range(k):
                    if(jTup[0] > data["simMatrix"][j][l][0]):
                        (sim, idx) = data["simMatrix"][j][l] 
                        data["simMatrix"][j][l] = jTup
                        jTup = (sim, idx)
                        l = k 
