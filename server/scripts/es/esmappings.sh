
idx='intellinews'
host="localhost:9200"
url=$host/$idx

echo 'url : ' 
echo $url
echo
curl -XPOST $url -d '{
    "settings" : {
    	"analysis" : {
		 "filter" : {
	    		"worddelim" : {
				"type" : "word_delimiter",
				"generate_word_parts" : "true",
				"split_on_case_change" : "true",
				"preserve_original": "true",
				"catenate_words": "true"
	    		},
			"name_ngrams" : {
                    		"side" : "front",
                    		"min_gram" : 4,
                    		"max_gram" : 10,
                    		"type" : "edgeNGram"
                	}  
		},   
		"analyzer" : {
	    		"default" : {
			 	"filter" : ["worddelim", "lowercase", "stop"],  
				"type": "custom",
				"tokenizer" : "standard",
				"char_filter": "html_strip"
	    		}  
		    }
	       
    	}
    } 
}'


curl -XPOST $url/doc/_mapping -d '{
  "doc" : {
        "properties" : {
	    "did": {"type" : "integer", "index" : "not_analyzed", "include_in_all":false},  
	    "crdate": {"type" : "date", "index" : "not_analyzed", "include_in_all":false}, 
        "type": {"type" : "string", "index" : "not_analyzed", "include_in_all":false} ,
	    "title": {"type" : "string", "index" : "analyzed"},
	    "content": {"type" : "string", "index":"analyzed"}   
        },  
	"_timestamp" : {
         "enabled" : true,
		 "include_in_all":false,
		 "store":"yes"
       }   
    }
}'


