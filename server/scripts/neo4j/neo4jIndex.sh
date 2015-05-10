host="localhost:7474"
url=$host

echo 'url : ' 
echo $url
echo	

curl -XPOST -H "Content-Type:application/json; charset=UTF-8;" $url/db/data/index/node/ -d '{
  "name" : "node_auto_index",
  "config" : {
    "type" : "fulltext",
    "provider" : "lucene"
  }
}'

curl -XPOST -H "Content-Type:application/json; charset=UTF-8;" $url/db/data/index/relationship/ -d '{
  "name" : "relationship_auto_index",
  "config" : {
    "type" : "fulltext",
    "provider" : "lucene"
  }
}'

curl -XPUT  -H "Content-Type:application/json; charset=UTF-8;"  $url/db/data/index/auto/node/status -d True

curl -XPOST  -H "Content-Type:application/json; charset=UTF-8;"  $url/db/data/index/auto/node/properties -d inm

curl -XPOST  -H "Content-Type:application/json; charset=UTF-8;"  $url/db/data/index/auto/node/properties -d index

curl -XPOST  -H "Content-Type:application/json; charset=UTF-8;"  $url/db/data/index/auto/node/properties -d itag

curl -XPOST  -H "Content-Type:application/json; charset=UTF-8;"  $url/db/data/index/auto/node/properties -d ictype

curl -XPOST  -H "Content-Type:application/json; charset=UTF-8;"  $url/db/data/index/auto/node/properties -d idid
