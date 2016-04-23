-- Get Nodes 

SELECT latitude, longitude, amenity, label 
FROM indiana_osm.current_nodes AS N 
	JOIN indiana_osm.current_node_tags AS T ON N.id = T.node_id 
    JOIN indiana_osm.amenity_label AS A ON T.v = A.amenity
WHERE k = 'amenity' AND 
longitude > -86.956787 AND longitude < -86.806412 AND latitude > 40.362765 AND latitude < 40.467845

UNION -- Get Ways

SELECT AVG(latitude) AS latitude, AVG(longitude) AS longitude, amenity, label
FROM indiana_osm.current_way_nodes AS W
	JOIN indiana_osm.current_nodes AS N ON N.id = W.node_id
    JOIN indiana_osm.current_way_tags AS WT ON W.id = WT.way_id 
    JOIN indiana_osm.amenity_label AS A ON WT.v = A.amenity
WHERE k = 'amenity' 
GROUP BY W.id
HAVING MAX(longitude) > -86.956787 AND MIN(longitude) < -86.806412 AND MAX(latitude) > 40.362765 AND MIN(latitude) < 40.467845