/**
	* UNOFFICIAL Client for library genesis (libgen.io)
	* m@tlin, 30.4.2017
	* v2 at 02.7.2017
	* usage: 
	* 	nodejs download-pdf.js [querry] // to list avaible results
	* 	nodejs download-pdf.js [querry] [outfile] [index] //to direct download
	*/

var request = require('request');
var fs = require('fs');
var cheerio = require('cheerio');
var readline = require('readline');

var request = request.defaults({jar: true});

///////////////////////////////////////////////////////////
// process the input
if (process.argv.length < 3) {
	throw ("Missing params, see comment in " + process.argv[1] + " to see usage");
}

var query = process.argv[2];
var outputFile = (process.argv.length > 4) ? process.argv[3] : null;
var itemIndex = (process.argv.length > 5) ? process.argv[4] : 0;

///////////////////////////////////////////////////////////
// utilities

var readFromConsole = function(promptText, readHandler) {
	console.log(promptText);
	
	var reader = readline.createInterface({
		  input: process.stdin,
		  output: process.stdout,
		  terminal: false
	});

	reader.on('line', function(line){
		var text = line.toString().trim();
		readHandler(text);
	});
}

var downloadFile = function(url, postData, outputFile) {
	console.log("Downloading to file " + outputFile + " (post: " + JSON.stringify(postData) + ")\n " + url);

	var file = fs.createWriteStream(outputFile);

	if (postData) {
//		request.post(url).form(postData).pipe(file);
		request.post({url: url, form: postData}, function(err, resp, body) {
			console.log(resp + ":"+  body);
			//TODO POST seems not implemented ...
		});
	} else {
		request(url).pipe(file);
	}

}



///////////////////////////////////////////////////////////
// working with urls

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

///////////////////////////////////////////////////////////////////////////////
// working with items

var getIthItem = function(items, itemIndex) {
	if (itemIndex >= items.length) {
		console.error(itemIndex + "th item does not exist, there is only " + items.length + " items avaible");
		return null;
	}

	var item = items[itemIndex];
	return item;
}


var printAllItems = function (items) {
	for (var i = 0; i < items.length; i++) {
		var item = items[i];
		console.log("[" + i + "] " + item.title + 
				"\n by " + item.author + " (" + item.pages + " pages, " + item.size + ")");
	}
}

///////////////////////////////////////////////////////////////////////////////
// download site processing

var findLinkOnSite = function(html, downloadLinkSelectorOrIndex) {
	var $ = cheerio.load(html);

	var $link;
	if (isNaN(downloadLinkSelectorOrIndex)) {
		$link = $(downloadLinkSelectorOrIndex);
	} else {
		$link	= $("a").eq(downloadLinkSelectorOrIndex);
	}

	return $link;
}

var findUrlOfLink = function($link) {
	return $link.attr("href");
}

var findFileDownloadUrl = function(html, downloadLinkSelectorOrIndex, baseUrl) {
	var $link = findLinkOnSite(html, downloadLinkSelectorOrIndex);
	if (!$link) {
		console.error("Error #3: " + "no download link on site");
		return null;
	}

	var url = findUrlOfLink($link, baseUrl);
	return url;
}

///////////////////////////////////////////////////////////////////////////////
// parsing of results 


var processHTML = function(html) {
	var $ = cheerio.load(html);
	var $table = $("table[width=\"1024\"]");
	var $rows = $table.children("tr");
	var $cells = $rows.children("td:first-child");	

	var items = [];
	$rows.each(function(e, index) {
		var $row = $(this);
		
		item = processEachRow($, $row, index);

		items.push(item);
	});

	return items;
}

var processEachRow = function($, $row, index) {
		var $tds = $row.children("td");
		
		var $sources = $tds.eq(0);
		var $author = $tds.eq(1);
		var $title = $tds.eq(2);
		var $infos = $tds.eq(5);
		var $size = $tds.eq(7);
	
//		console.log($author.text() + ":: " + $title.text());
		var author = $author.text();
		var title = $title.text();

		var libgen = processSourcesOfRow($, $sources, index);
		var pages = processInfosOfRow($, $infos, index);
		var size = $size.text();

		var item = { "author": author, "title": title, "url": libgen, "pages": pages, "size": size};
		return item;
}

var processSourcesOfRow = function($, $sources, index) {
		var $links = $sources.find("a");	

		var libgen = null;
		$links.each(function(e) {
			if (source != null) {
				return;
			}

			var $link = $(this);
			var source = $link.text();
			if (source == "Libgen") {
				var url = $link.attr("href");

				var normalized = normalizeItemUrl(url);
				libgen = normalized;	
			}
		});
		
		if (libgen == null) {
			console.warn("Item on index " + index + " has no " + "Libgen" + " source");
		}
		
		return libgen;
}

var processInfosOfRow = function($, $infos, index) {
	var infosStr = $infos.html();
	var parts = infosStr.split("<br>");

	var firstPagePart = parts[5];
	var lastPagePart = parts[6];

	var firstPage = firstPagePart.split(":")[1];
	var lastPage = lastPagePart.split(":")[1];
	
	// console.log(firstPage + "~" + lastPage);
	if (isNaN(firstPage) || isNaN(lastPage)) {
		console.warn("Item with index " + index + " has unspecified pages range");
		return 0;
	} else {
		return lastPage - firstPage;
	}
}
///////////////////////////////////////////////////////////////////////////////
// download handlers

var processItem = function(item, outputFile) {
	console.log("Downloading '" + item.title + "' by '" + item.author + "' \t from " + item.url);
	
	var downloadHandler =  function(error, response, body) {
		if (error) {
			console.error("Error #2: " + error);
			return;
		} else {
			var url = findFileDownloadUrl(body, 1);
			if (url) {	
				downloadFile(url, null, outputFile);
			}
		}
	}

	request.get(item.url, downloadHandler);
}

var doTheQuery = function(query, outputFile, itemIndex) {
	var url = constructQueryUrl(query);
	
	var queryHandler =  function(error, response, body) {
		if (error) {
			console.error("Error #1: " + error);
			return;
		} else {
			var items = processHTML(body);
			console.log("Found " + items.length + " items");
			if (outputFile) {
				var item = getIthItem(items, itemIndex);
				if (!item) {
					return;
				}
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


doTheQuery(query, outputFile, itemIndex);


