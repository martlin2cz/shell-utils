/**
	* UNOFFICIAL Client for library genesis (libgen.io)
	* m@tlin, 30.4.2017
	*/

var request = require('request');
var fs = require('fs');
var cheerio = require('cheerio');


///////////////////////////////////////////////////////////
// process the input
if (process.argv.length < 2) {
	throw new Exception("Missing params");
}

var query = process.argv[2];
var outputFile = (process.argv.length > 2) ? process.argv[3] : null;
var itemIndex = (process.argv.length > 2) ? process.argv[4] : 0;
var sourceIndex = (process.argv.length > 2) ? process.argv[5] : 0;

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

var getIthItem = function(items, itemIndex, sourceIndex) {
	if (itemIndex >= items.length) {
		console.error(itemIndex + "th item does not exist, there is only " + items.length + " items avaible");
		return null;
	}

	var item = items[itemIndex];
	
	if (sourceIndex >= item.sources.length) {
		console.error(itemIndex + "th source does not exist, there is only " + item.source.length + " sources avaible");
		return null;
	}

	var source = item.sources[sourceIndex];

	return { "title": item.title, "author": item.author, "source": source.source, "url": source.url };
}


var printAllItems = function (items) {
	for (var i = 0; i < items.length; i++) {
		var item = items[i];
		console.log("[" + i + "] " + item.title + " (" + item.author + ")");
		
		for (var j = 0; j < item.sources.length; j++) {
			var source = item.sources[j];
			console.log("\t[" + j + "] " + source.source + ": " + source.url);
		}
	}
}

var processHTML = function(html) {
	var $ = cheerio.load(html);
	var $table = $("table[width=\"1024\"]");
	var $rows = $table.children("tr");
	var $cells = $rows.children("td:first-child");	

	var items = [];
	$rows.each(function(e) {
		var $row = $(this);
		var $tds = $row.children("td");
		
		var $sources = $tds.eq(0);
		var $author = $tds.eq(1);
		var $title = $tds.eq(2);
		
//		console.log($author.text() + ":: " + $title.text());
		var author = $author.text();
		var title = $title.text();

		var $links = $sources.find("a");	
		var sources = [];
		$links.each(function(e) {
			var $link = $(this);
			var source = $link.text();
			var url = $link.attr("href");

			var normalized = normalizeItemUrl(url);
			var path = { "source": source, "url": normalized };
 	 		sources.push(path);
		});


		var item = { "author": author, "title": title, "sources": sources };
		items.push(item);
	});

	return items;
}

var processItem = function(item, outputFile) {
	console.log("Downloading '" + item.title + "' by '" + item.author + "' from " + item.source + "\n" + item.url);
	
	var stream = fs.createWriteStream(outputFile);
	request(item.url).pipe(stream);
}

var doTheQuery = function(query, outputFile, itemIndex, sourceIndex) {
	var url = constructQueryUrl(query);
	
	var queryHandler =  function(error, response, body) {
		if (error) {
			console.error("Error #1: " + error);
			return;
		} else {
			var items = processHTML(body);
			console.log("Found " + items.length + " items");
			if (outputFile) {
				var item = getIthItem(items, itemIndex, sourceIndex);
				processItem(item, outputFile);
			} else {
				printAllItems(items);
			}
		}
	}

	request.get(url, queryHandler);
}


///////////////////////////////////////////////////////////
// run the main function


doTheQuery(query, outputFile, itemIndex, sourceIndex);


