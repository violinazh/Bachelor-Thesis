CALL spatial.importOSM("/home/vzh/Downloads/neo4j-community-3.5.0/import/berlin.osm");

MATCH (n:Person)
DETACH DELETE n

MATCH (c:Category)
WHERE c.name IS NULL
SET c.name = c.title
REMOVE c.title

DROP INDEX/CONSTRAINT

Vertices:

-CREATE CONSTRAINT ON (c:CROSSROAD) ASSERT c.id IS UNIQUE;

USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM "file:///RoadVerticesBER.csv" AS row
CREATE (p:CROSSROAD {id: toInteger(row.VertexId), long: toFloat(row.Longitude), lat: toFloat(row.Latitude)});

CREATE INDEX ON :CROSSROAD(id);

Edges:

-CREATE CONSTRAINT ON (r:ROAD) ASSERT r.id IS UNIQUE;

USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM "file:///RoadEdgesBER.csv" AS row
MATCH (start_node:CROSSROAD {id: toInteger(row.startVertixId)})
MATCH (end_node:CROSSROAD {id: toInteger(row.endVertixId)})
CREATE (start_node)-[r:ROAD]->(end_node)
SET r.id = toInteger(row.EdgeId);

MATCH (a:CROSSROAD)-[r:ROAD]->(b:CROSSROAD)
SET r.distance = distance(point({ longitude: a.long, latitude: a.lat }), point({ longitude: b.long, latitude: b.lat})),
r.start_node = a.id,
r.end_node = b.id;

CREATE INDEX on :ROAD(start_node);
CREATE INDEX on :ROAD(end_node);

POIs:

CREATE INDEX on :POI(id);
CREATE INDEX on :POI(type);

USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM "file:///RestaurantsBER.csv" AS row
CREATE (p:POI)
SET p.id = toInteger(row.POIId),
p.type = ["restaurant"],
p.crossroad = toInteger(row.EdgeId),
p.lat = toFloat(row.Latitude),
p.long = toFloat(row.Longitude),
p.dist = toFloat(row.Distance_from_start_node);

MATCH (:CROSSROAD)-[h:HAS_POI]->(:POI)
SET h.distance = 0

-> Checking for duplicates
LOAD CSV WITH HEADERS FROM "file:///CoffeeShopsBER.csv" AS row
MERGE (p:POI {crossroad:toInteger(row.EdgeId), lat:toFloat(row.Latitude), long:toFloat(row.Longitude), dist:toFloat(row.Distance_from_start_node)})
ON MATCH SET p.type = p.type + "coffee_shop"
ON CREATE SET p.type = ["coffee_shop"],
p.id = toInteger(row.POIId)

-> Mapping the POIs to start or end node conditionally
MATCH (p:POI)
MATCH (a:CROSSROAD)-[r:ROAD {id:p.crossroad} ]->(b:CROSSROAD)
FOREACH (ignoreMe in CASE
WHEN (p.dist <= 0.5) THEN [1]
ELSE [] END | CREATE (a)-[h:HAS_POI]->(p) SET h.dist = p.dist)
FOREACH (ignoreMe in CASE
WHEN (p.dist > 0.5) THEN [1]
ELSE [] END | CREATE (b)-[h:HAS_POI]->(p) SET h.dist = p.dist)

-MATCH (p:POI)
MATCH (a:CROSSROAD)-[r:ROAD {id:p.crossroad} ]->(b:CROSSROAD)
CREATE (a)-[h:HAS_POI]->(p)

-USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM "file:///RestaurantsBER.csv" AS row
MATCH (a:CROSSROAD)-[h:HAS_POI]->(p:POI {id:toInteger(row.POIId), type: "restaurant"})
SET h.dist = toFloat(row.Distance_from_start_node);

--------------------------------------------------------------------------
Queries:

(1) Which crossroad has the most points of interest and in which category do they belong (category name and number of pois for every category)? Sort them in descending order?

MATCH (a:CROSSROAD)-[h:HAS_POI]->(p:POI)
WITH a.id AS id, count(h) AS degree, collect(p.type) AS nameList
UNWIND nameList AS name
WITH id, degree, name, count(*) AS count
ORDER BY count DESC
WITH id, degree, collect({category_name:name, number_of_pois:count}) AS list
RETURN id, degree, list
ORDER BY degree DESC

(2, 3) Which is the shortest path and length between crossroads with id:10 and id:16?

MATCH path = allshortestPaths((start_node:CROSSROAD {id:10})-[ROAD*]-(end_node:CROSSROAD {id:16}))
RETURN length(path) as length, path

(4) Find the top three crossroads with the most bars.

MATCH (a:CROSSROAD)-[h:HAS_POI]-(p:POI {type: "pub_bar"})
RETURN a.id, count(h) AS degree
ORDER BY degree DESC
limit 3

(5) Which is the shortest path between crossroads with id:10 and id:21 which passes through crossroad with id:17?

MATCH path1 = shortestPath((a:CROSSROAD {id:10})-[r1:ROAD*]-(c:CROSSROAD {id:17}))
MATCH path2 = shortestPath((c:CROSSROAD {id:17})-[r2:ROAD*]-(b:CROSSROAD {id:21}))
RETURN path1, path2, length(path1) + length(path2) AS length
ORDER by length DESC
limit 1

(6) Find the five closest crossroads to the point with Latitude: 39 and Longitude: -123.

!Euclidean distance

MATCH (o:CROSSROAD)
WITH ({id:'POINT', long:-123, lat:39}) AS p1,
({id:o.id, long:o.long, lat:o.lat}) AS p2
RETURN p1 AS point, p2 AS nearestCrossroads, sqrt((p1.long-p2.long)^2 + abs(p1.lat-p2.lat)^2) AS dist
ORDER BY dist
limit 5

-> Finding the number of POIs mapped to a node:

MATCH p=(a:CROSSROAD)-[r:HAS_POI]->() 
RETURN a.id, count(r) AS count
ORDER BY count DESC

-> Travel distance between two crossroad/POI points:

MATCH (start:CROSSROAD{id:10}), (end:CROSSROAD{id:16})
CALL algo.shortestPath.stream(start, end, 'distance')
YIELD nodeId, cost
RETURN algo.getNodeById(nodeId).id AS id, cost

MATCH (a:CROSSROAD)-[k:HAS_POI]->(o:POI {id: 10, type: "coffee_shop"})
MATCH (c:CROSSROAD)-[h:HAS_POI]->(p:POI {id: 4, type: "restaurant"})
CALL algo.shortestPath(a, c, 'distance')
YIELD totalCost
RETURN p.id as POI, totalCost

-> Finding PoIs from specific category:

MATCH (p:POI) WHERE p.type = "restaurant" RETURN p

+ When type is a array
MATCH (p:POI) WHERE ANY(someid IN p.type WHERE someid = "restaurant")
RETURN p

-> Find all category types
- as list
MATCH (p:POI)
WITH collect(DISTINCT p.type) AS poitypes
UNWIND poitypes AS poitype
RETURN poitype

- separately
MATCH (p:POI)
WITH collect(DISTINCT p.type) AS poitypes
UNWIND poitypes AS poitype
UNWIND poitype AS type
WITH DISTINCT type
RETURN type

-> Calculating the nearest neighbour of a point from a specific category:

(!Euclidean distance) MATCH (a:CROSSROAD)-[k:HAS_POI]->(o:POI {id: 10, type: "coffee_shop"})
MATCH (c:CROSSROAD)-[h:HAS_POI]->(p:POI {type: "restaurant"})
RETURN c AS nearestRestaurants, sqrt((a.long-c.long)^2 + abs(a.lat-c.lat)^2) AS dist
ORDER BY dist
limit 5

-Takes too much time to execute for every node and type
MATCH (a:CROSSROAD)-[k:HAS_POI]->(o:POI {id: 10})
MATCH (c:CROSSROAD)-[h:HAS_POI]->(p:POI {type: "restaurant"})
CALL algo.shortestPath(a, c, 'distance')
YIELD totalCost
RETURN p.id as POI, totalCost
ORDER BY totalCost
limit 1

MATCH (a:CROSSROAD)-[k:HAS_POI]->(o:POI {id: 10})
MATCH (p:POI) WHERE ANY(someid IN p.type WHERE someid = "movie_theater")
MATCH (c:CROSSROAD)-[h:HAS_POI]->(p)
CALL algo.shortestPath(a, c, 'distance')
YIELD totalCost
RETURN p.id as POI, totalCost
ORDER BY totalCost
limit 1

- Alternative solution, but number of hops unknown in advance
MATCH poipath = (c1:CROSSROAD)-[r:ROAD*0..30]->(c2:CROSSROAD)-->(p:POI)
WHERE c1.id = 178732
WITH c1, p, reduce(total=0, h in relationships(poipath) | total + h.distance) AS totalCost
WITH c1, p.type AS poitype, min(totalCost) AS minCost
RETURN poitype, minCost
ORDER BY minCost

- With pid included and type simple
MATCH poipath = (c1:CROSSROAD)-[r:ROAD*0..30]->(c2:CROSSROAD)-->(p:POI)
WHERE c1.id = 178732
WITH c1, p, reduce(total=0, h in relationships(poipath) | total + h.distance) AS totalCost
WITH c1, p.id as pid, p.type AS poitype, min(totalCost) AS minCost
UNWIND poitype as type
RETURN head(collect(pid)), type, min(minCost)


For JAVA:

- For every crossroad find the pois
MATCH (a:CROSSROAD {id:189146})-[r:HAS_POI]->(p:POI)
UNWIND p.type as type
RETURN a.id, p.id, type, r.dist

- Find all roads
MATCH (a:CROSSROAD)-[r:ROAD]->(b:CROSSROAD) 
RETURN a.id, r.distance, b.id







