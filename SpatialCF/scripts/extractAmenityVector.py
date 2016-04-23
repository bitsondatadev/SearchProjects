import xml.etree.ElementTree as ET
import re

amenities = set()
stopwords = ["the", "of"]

print "Loading Amenities...\n"
tree = ET.parse("..\\data\\tippecanoe.osm")
root = tree.getroot()
for el in root.iter():
	if el.tag == "tag" and el.attrib["k"] == "amenity": 
		amenities.add(re.sub('[_]', ' ', el.attrib["v"])) 

print "Finished Loading Amenities!! Writing Ammenity Vector File...\n"
amenities = sorted(amenities)
output = open("..\\data\\amenityVector.txt", 'w')
for amenity in amenities:
	tempStr = ""
	for a in amenity.split():
		if not a in stopwords:
			tempStr += (a + " ") 
	print tempStr
	output.write(tempStr + "\n")
print "Successful Amenity File Creation!!"
output.close()