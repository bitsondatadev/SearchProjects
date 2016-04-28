# CS 54701 Project 3: Spatial Recommendation System.
Spatial information retrieval (SIR) is an extension of the well studied information retrievaltopic which focuses on evaluating a user query and returning documents that satisfy this user's information need. SIR aims to accomplish the same objective but with regard to spatial proximity specied in the query of the user. An increasingly popular technique called collaborative filtering has gained much popularity with the increasing e-commerce applications that drive a personalized experience for the user. Collaborative filtering uses prior data from similar users to suggest possible items that the user has not tried yet. In the same manner we have similar types of recommendation systems for spatial systems today that track multiple users spatiotemporal activity through check-in data via microblog sites such as Twitter and Foursquare.

**Example:** Consider the following scenario where a user is out of town and wants to go out for entertainment and opens up an app to look for something to do. Instead of knowing specifically what the user wants to do he or she just wants to be in the general area and figure out the specifics once they're there. If the user tends to go to clubs there are most likely other users that do the same thing. Based on the types of locations the other users go to we can suggest a generic area of interest for our user to get their night started.

## Data wrangling

First I needed to obtain and preprocess the data accordingly. My two sources of data are from [Open Street Maps (OSM)](http://www.openstreetmap.org/)  and  [Twitter](https://twitter.com/) data. I believe the primary hurdle in terms of data aggregation and processing would be classifying and labeling areas or clusters of nodes in the OSM data. 
### Getting the data
#### OSM
1. Since I am limiting my evaluation to Tippecanoe county, I decided to first download a subset of the OSM data ([indiana.osm.pbf](http://download.geofabrik.de/north-america/us/indiana.html)).
1. I then downloaded and installed a java cli processing application for OSM data called [Osmosis](http://wiki.openstreetmap.org/wiki/Osmosis). This application can be used to filter out data and convert data into a different format or store it into a database. 
    1. Before storing the data into the database I had to set up the MySQL database and create the tables. Unfortunately MySQL isn't officially supported anymore but luckily someone had posted [an old schema](https://github.com/oschrenk/osmosis-mysql/blob/master/mysql-apidb06.sql) and I doctored it to hold the data I needed. 
    1. I ran the following command using osmosis to store it in a mysql:<br/>
        ```sh
        $ osmosis \<br/>
        --read-pbf ..\data\indiana.osm.pbf \<br/>
        --write-apidb host="127.0.0.1" dbType="mysql" database="indiana_osm" \<br/>
        user="*******" password="*******" validateSchemaVersion=no<br/>
        ```
		<br/>
    1. Osmosis didn't store latitude and longitude as decimals but instead as giant integers (e.g. -87.1234567 became -871234567.00). So to get around this I stored them as big decimals and divided the latitude/longitude columns by 10000000.
    1. From the database I specified the query below using the bounding box left=-86.956787 bottom=40.362765 right=-86.806412 top=40.467845 to surround approximately the boundary of Tippecanoe county.
        ```sql
        -- Get Nodes 
        SELECT latitude, longitude, amenity, label 
        FROM indiana_osm.current_nodes AS N 
	        JOIN indiana_osm.current_node_tags AS T ON N.id = T.node_id 
            JOIN indiana_osm.amenity_label AS A ON T.v = A.amenity
        WHERE k = 'amenity' AND longitude > -86.956787 AND longitude < -86.806412 AND latitude > 40.362765 AND latitude < 40.467845
        UNION -- Get Ways
        SELECT AVG(latitude) AS latitude, AVG(longitude) AS longitude, amenity, label
        FROM indiana_osm.current_way_nodes AS W
	        JOIN indiana_osm.current_nodes AS N ON N.id = W.node_id
            JOIN indiana_osm.current_way_tags AS WT ON W.id = WT.way_id 
            JOIN indiana_osm.amenity_label AS A ON WT.v = A.amenity
        WHERE k = 'amenity' 
        GROUP BY W.id
        HAVING MAX(longitude) > -86.956787 AND MIN(longitude) < -86.806412 AND MAX(latitude) > 40.362765 AND MIN(latitude) < 40.467845
        ```
    
The resulting dataset is in the following form and is saved in [osm_tippecanoe_2016.csv](https://raw.githubusercontent.com/brianolsen87/SearchProjects/master/SpatialCF/data/osm_tippecanoe_2016.csv).
| latitude | longitude | amenity | label |
|----------|-----------|---------|-------|
|          |           |         |       |

#### Twitter
Fortunately for me, my lab has access to Twitter data and I was able to query and export this data using the following command on the SQLCMD tool.
```sh
    $ sqlcmd -S <server_name>.purdue.edu -d <database_name> -U <user_name> -P <password> -W \
    -Q "SET NOCOUNT ON SELECT 
    [tweet_id], [created_at], [geo_lat], [geo_long], [user_id], 
    REPLACE(REPLACE([tweet_text], CHAR(13), ''), CHAR(10), '') 
    From dbo.tweet_us_2016_1_3  
    WHERE [geo_long] >= -86.956787 AND [geo_long] <= -86.806412 AND 
          [geo_lat] >= 40.362765 AND [geo_lat] <= 40.467845  
    ORDER BY created_at;" \
    -o \\<output_location>\tweet_tippecanoe_2016_1_3.csv -h-1 -s"," -f 65001
```
        
The resulting dataset is in the following form and is saved in [tweet_tippecanoe_2016_1_3.csv](https://raw.githubusercontent.com/brianolsen87/SearchProjects/master/SpatialCF/data/tweet_tippecanoe_2016_1_3.csv). 
| tweet_id | timestamp | latitude | longitude | user_id | text |
|----------|-----------|----------|-----------|---------|------|
|          |           |          |           |         |      |
### Failed attempt
It seems like we could get a sense of what a particular node entity was to classify the areas by looking at the "amenity" tag defined in the OSM data. I initially pulled out a vector of all the amenities that showed up in Tippecannoe county and mapped tweets that contained these words onto this vector space using the term frequencies. I performed a K-means clustering with k=8 to try and map amenities to topics. The problem was that the vector space was too small and specific and it seemed I would get most terms clustering in one or two topics. 
### Resolution
I reevaluated what would be important to the evaluation versus the end result being actually usable. In theory as open street maps evolves and they expand their labels using this data would better realize usable data but for the context of this course I discussed with the professor and asked if I could just use the [simple catagories suggested by the open street map wiki](http://wiki.openstreetmap.org/wiki/Key:amenity) and he said it would be fine. That being said, while the actual suggestions being made may not make sense, in the end we will simply evaluate which model gives a better scoring versus what makes better sense in the real world.
### 