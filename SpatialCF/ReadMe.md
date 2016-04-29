# CS 54701 Project 3: Spatial Recommendation System.
Spatial information retrieval (SIR) is an extension of the well studied information retrievaltopic which focuses on evaluating a user query and returning documents that satisfy this user's information need. SIR aims to accomplish the same objective but with regard to spatial proximity specied in the query of the user. An increasingly popular technique called collaborative filtering has gained much popularity with the increasing e-commerce applications that drive a personalized experience for the user. Collaborative filtering uses prior data from similar users to suggest possible items that the user has not tried yet. In the same manner we have similar types of recommendation systems for spatial systems today that track multiple users spatial activity through check-in data via microblog sites such as Twitter and Foursquare.

**Example:** Consider the following scenario where a user is out of town and wants to go out for entertainment and opens up an app to look for something to do. Instead of knowing specifically what the user wants to do he or she just wants to be in the general area and figure out the specifics once they're there. If the user tends to go to clubs there are most likely other users that do the same thing. Based on the types of locations the other users go to we can suggest a generic area of interest for our user to get their night started.

## Data wrangling

First I needed to obtain and preprocess the data accordingly. My two sources of data are from [Open Street Maps (OSM)](http://www.openstreetmap.org/)  and  [Twitter](https://twitter.com/). I believe the primary hurdle in terms of data aggregation and processing would be classifying and labeling areas or clusters of nodes in the OSM data. 
### Getting the data
#### OSM
1. Since I am limiting my evaluation to Tippecanoe county, I decided to first download a subset of the OSM data ([indiana.osm.pbf](http://download.geofabrik.de/north-america/us/indiana.html)).
1. I then downloaded and installed a java cli processing application for OSM data called [Osmosis](http://wiki.openstreetmap.org/wiki/Osmosis). This application can be used to filter out data and convert data into a different format or store it into a database. 
    1. Before storing the data into the database I had to set up the MySQL database and create the tables. Unfortunately MySQL isn't officially supported anymore but luckily someone had posted [an old schema](https://github.com/oschrenk/osmosis-mysql/blob/master/mysql-apidb06.sql) and I doctored it to hold the data I needed. 
    1. I ran the following command using osmosis to store it in a mysql:<br/>
        ``` $ osmosis \```<br/>
        ``` --read-pbf ..\data\indiana.osm.pbf \```<br/>
        ``` --write-apidb host="127.0.0.1" dbType="mysql" database="indiana_osm" \```<br/>
        ``` user="*******" password="*******" validateSchemaVersion=no```<br/>
        
    1. Osmosis didn't store latitude and longitude as decimals but instead as giant integers (e.g. -87.1234567 became -871234567.00). So to get around this I stored them as big decimals and divided the latitude/longitude columns by 10000000.
    1. From the database I specified the query below using the bounding box left=-86.956787 bottom=40.362765 right=-86.806412 top=40.467845 to surround approximately the boundary of Tippecanoe county.<br/>
        ```-- Get Nodes ```<br/>
        ```SELECT latitude, longitude, amenity, label ```<br/>
        ```FROM indiana_osm.current_nodes AS N ```<br/>
	    ```    JOIN indiana_osm.current_node_tags AS T ON N.id = T.node_id ```<br/>
        ```    JOIN indiana_osm.amenity_label AS A ON T.v = A.amenity```<br/>
        ```WHERE k = 'amenity' AND longitude > -86.956787 AND longitude < -86.806412 AND latitude > 40.362765 AND latitude < 40.```<br/>
        ```UNION -- Get Ways```<br/>
        ```SELECT AVG(latitude) AS latitude, AVG(longitude) AS longitude, amenity, label```<br/>
        ```FROM indiana_osm.current_way_nodes AS W```<br/>
	    ```    JOIN indiana_osm.current_nodes AS N ON N.id = W.node_id```<br/>
        ```    JOIN indiana_osm.current_way_tags AS WT ON W.id = WT.way_id ```<br/>
        ```    JOIN indiana_osm.amenity_label AS A ON WT.v = A.amenity```<br/>
        ```WHERE k = 'amenity' ```<br/>
        ```GROUP BY W.id```<br/>
        ```HAVING MAX(longitude) > -86.956787 AND MIN(longitude) < -86.806412 AND MAX(latitude) > 40.362765 AND MIN(latitude) < 40.467845```<br/>

    
The resulting dataset is in the following form and is saved in [osm_tippecanoe_2016.csv](https://raw.githubusercontent.com/brianolsen87/SearchProjects/master/SpatialCF/data/osm_tippecanoe_2016.csv).

| latitude | longitude | amenity | label |
|----------|-----------|---------|-------|
|          |           |         |       |

##### Failed attempt
It seems like we could get a sense of what a particular node entity was to classify the areas by looking at the "amenity" tag defined in the OSM data. I initially pulled out a vector of all the amenities that showed up in Tippecannoe county and mapped tweets that contained these words onto this vector space using the term frequencies. I performed a K-means clustering with k=8 to try and map amenities to topics. The problem was that the vector space was too small and specific and it seemed I would get most terms clustering in one or two topics. 
##### Resolution
I reevaluated what would be important to the evaluation versus the end result being actually usable. In theory as open street maps evolves and they expand their labels using this data would better realize usable data but for the context of this course I discussed with the professor and asked if I could just use the [simple categories suggested by the open street map wiki](http://wiki.openstreetmap.org/wiki/Key:amenity) and he said it would be fine. That being said, while the actual suggestions being made may not make sense, in the end we will simply evaluate which model gives a better scoring versus what makes better sense in the real world.


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

#### Combined datasets

Once I had both datasets I wrote [a python script](https://raw.githubusercontent.com/brianolsen87/SearchProjects/master/SpatialCF/scripts/combine_data.py) that took the kNN of the tweet data where k=4 (due to the average size of the amenity clusters). If there was a tie in the number of qualifying labels I would increase k on a unit by unit basis until a winner was found. The resulting dataset was put in the following schema and is saved under [tweet_label_tippecanoe_2016.csv](https://raw.githubusercontent.com/brianolsen87/SearchProjects/master/SpatialCF/data/tweet_label_tippecanoe_2016.csv). As a preprocessing step I manually went through and classified 35 tweet bots that were posting job posts and weather updates from the same location. After removing these users we have are 1,107 users and 6,073 tweets meaning about an average of 6 tweets per user. In my evaluation I have chosen varied representations of 10 users based on their tweet frequency. I made sure the user had at least 10 tweets.

| user_id | latitude | longitude | label | 
|---------|----------|-----------|-------|
|         |          |           |       |


## Method Descriptions
The two methods I will be comparing is one that I thought may be  a good idea and I am comparing it with a common kernel-topic model. In this evaluation we are primarily focused on leveraging the spatial data alone. The text of the tweet will not be considered in either model. Other than using the spatial dimension we use the amenity labeled open street map data to provide us context of the location rather than tweet text. <br/>

The kernel-topic model is a balanced model that was a close contender to a novel statistical collaborative filtering technique proposed in a [paper I found](https://github.com/brianolsen87/SearchProjects/blob/master/SpatialCF/papers/Geo%20Topic%20Model%20Joint%20Modeling%20of%20User%E2%80%99s%20Activity%20Area%20and%20Interests%20for%20Location%20Recommendation.pdf). While the paper is introducing a much more advanced model, this model focuses too much on using the twitter text to use the topic data as a means to find more related areas of interest to the user. As stated above, we are using labeled data from OSM instead of using tweet data to provide context of the geographic location the user is tweeting from. This will provide more of a focus on the geo-spatial data and geo-spatial features rather than introduce complex ideas of tweet text. We reference formulas, 10, 11, and 12 in the paper and will elaborate more on how we used the formulas in the formulas.pdf. <br/>

To choose an alpha and a Beta I ran the model using various values for each and it seemed that a small alpha and beta worked best on the county sized data. I chose to use alpha = .25 and beta = 100. <br/>

|     MSE     | alpha | beta |
|-------------|-------|------|	
| 0.964251088 |	0.25  |	100  |
| 1.923318075 |	0.25  | 1000 |
| 2.849659601 |	0.25  | 10000|
| 3.816759893 |	0.5   | 100  |
| 4.773470899 |	0.5   | 1000 |
| 5.665687612 |	0.5   | 10000|
| 6.636313799 |	0.75  | 100  |
| 7.591324429 |	0.75  | 1000 |
| 8.451028568 |	0.75  | 10000|


My approach is that instead of using a statistical model I plan on applying a collocation pattern to the data. Recently there have been many advances in spatial data mining that seek to find collocation patterns using approaches that [piggyback off of association-pattern mining](https://github.com/brianolsen87/SearchProjects/blob/master/SpatialCF/papers/Discovering%20Colocation%20Patterns%20from%20Spatial%20Data%20Sets%20%20-%20A%20General%20Approach.pdf). While association-pattern mining has been [applied to non-spatial data](https://github.com/brianolsen87/SearchProjects/blob/master/SpatialCF/papers/Effective%20Personalization%20Based%20on%20Association%20Rule%20Discovery%20from%20Web%20Usage%20Data.pdf) to provide ranking for collaborative filtering using support and confidence measures to provide a ranking for collaborative filtering, these methodologies have yet to be applied in spatial collaborative filtering. I feel confident that this approach will work as the research for the association rules applied to spatial data have already been realized and we can marry the two ideas. For instance, we know that spatial data is not anti-monotonous and this ruins fundamental pruning advantages from traditional pattern mining. We can apply the current research using a modified pattern mining approach. I will finally rank the items by the one's with either highest support, confidence or both. It is hard to say if this approach will be more effective but I believe since pruning is a key element in this algorithm we may be at the least more proficient in the computation than the kernel-topic model above. <br/>

In short the way I will apply my model is to use a ratio

## Evaluation
To evaluate the models performance against one another I will use k-cross folds validations and apply mean squared error in my prediction rate.

###Kernel-topic model results
| user_id    | MSE      |
|------------|----------|
| 388997369  | 0.686082 |
| 2350966291 | 0.929231 |
| 44524722   | 0.96293  |
| 55862979   | 0.985353 |
| 48134589   | 0.493049 |
| 205530091  | 0.581644 |
| 1925340810 | 0.977743 |
| 20168184   | 0.964251 |
| 22896762   | 0.986836 |
| 136798620  | 0.809144 |

The average prediction rate over the different users was 0.8376. <br/>

## Discussion
All in all I felt like I accomplished my goal which was to devise a scenario to evaluate association-pattern rule mining applied to spatial collaborative filtering and compare that method with common methods used today. 