import re, math
from sklearn.cluster import KMeans

#read in amenity vector
input = open("data\\amenityVector.txt", 'r')
amenityVector = []
for line in input:
	amenityVector.append(line.rstrip())

#Read in 220,128,795 tweets
#but only require numTweets to qualify
input = open("Z:\\tweet_us_2016_1_3.csv", 'r')
matrix = []
numTweets = 100000000.0
percentDivisor = numTweets / 100
hasPrinted = False
for line in input:
	csvLine = line.split(',')
	if len(csvLine) < 3:
		continue
	tweetArray = csvLine[2].strip().split()
	newRow = []
	numMatches = 0
	for amenity in amenityVector:
		cnt = sum(tweetArray.count(s) for s in amenity.split())
		if cnt > 0:
			numMatches += 1
		newRow.append(cnt)
		
	#Keep where the number of  word matches are more than one
	#to strictly model where two amenities show up together in the data.
	if numMatches > 1:
		norm = 0.0
		for v in newRow:
			norm += (v * v)
		norm = math.sqrt(norm)
		for i in range(len(newRow)):
			newRow[i] = newRow[i]/norm
		matrix.append(newRow)
		
	if len(matrix) >= numTweets:
		break
	if len(matrix) % percentDivisor == 0 and not hasPrinted:
		print str((len(matrix) / numTweets) * 100) + "% finished."
		hasPrinted = True
	elif len(matrix) % percentDivisor != 0:
		hasPrinted = False
input.close()

#Generate amenityMatrix, which is just just an identity matrix
amenityMatrix = [[1 if cid == rid else 0 for cid in range(len(amenityVector))] for rid in range(len(amenityVector))]

#Generate KMeans Cluster on tweet/amenity matrix 
k_means = KMeans(init='k-means++', n_clusters=8, n_init=10)
k_means.fit(matrix)

#Cluster using the identity matrix to see what clusters each amenity is closest to.
cids = list(k_means.predict(amenityMatrix))

#Make dictionary to hold each cluster
clusters = {}
for i in range(len(cids)):
	if cids[i] not in clusters:
		clusters[cids[i]] = []
	clusters[cids[i]].append(amenityVector[i])

#Write clusters to different lines in csv format
output = open("data\\clusters.csv", 'w')
for k in clusters:
	str = ""
	for v in clusters[k]:
		str += (v + ",")
	output.write(str + "\n")
output.close()