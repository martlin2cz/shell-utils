/**
	* UNOFFICIAL Client for library genesis (libgen.io)
	* m@tlin, 30.4.2017
	*/

var request = require('request');
var cheerio = require('cheerio');


///////////////////////////////////////////////////////////
// process the input
if (process.argv.length < 3) {
	throw new Exception("Missing params");
}

var query = process.argv[2];
var output = process.argv[3];
var index = 0;	//TODO ?

console.log("Querying " + query + "...");

///////////////////////////////////////////////////////////
// handlers

var constructQueryUrl = function (query) {
	return "http://libgen.io/scimag/index.php" 
		+ "?s=" + query;
		+ "&journalid="
		+ "&v="
		+ "&i="
		+ "&p="
		+ "&redirect=0";
}

var normalizeItemUrl = function(url) {
	if (url.indexOf("http://") == -1) {
		return "http://libgen.io" + url;
	} else {
		return url;
	}
}

var processHTML = function(html) {
	var $ = cheerio.load(html);
	var $table = $("table[width=\"1024\"]");
	var $rows = $table.children("tr");
	var $cells = $rows.children("td:first-child");	

	var $tables = $cells.children("table");
	var $links = $tables.find("a");
	
	var urls = [];
	$links.each(function(e) {
		var $link = $(this);
		var source = $link.text();
		var url = $link.attr("href");

		var normalized = normalizeItemUrl(url);
		var item = {"source": source, "url": normalized };
  	urls.push(item);
	});

	console.log(urls);

	return urls;
}

var processItemLink = function(url) {
	var downloadHandler =  function(error, response, body) {
		if (error) {
			console.error("Error #1: " + error);
			return;
		} else {
	
		//TODO save file
		}
	}

	request.get(url, downloadHandler);
}

var doTheQuery = function(query, output, index) {
	var url = constructQueryUrl(query);
	
	var queryHandler =  function(error, response, body) {
		if (error) {
			console.error("Error #1: " + error);
			return;
		} else {
			var items = processHTML(body);
			console.log("Found " + items.length + " items");
			var item = items[index];
			processItemLink(item);
		}
	}

	request.get(url, queryHandler);
}


///////////////////////////////////////////////////////////
// run the main function


doTheQuery(query, output, index);


