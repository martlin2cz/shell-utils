/**
	* UNOFFICIAL Client for library genesis (libgen.io)
	* m@tlin, 30.4.2017
	*/

var request = require('request');
var fs = require('fs');
var cheerio = require('cheerio');
var readline = require('readline');

var request = request.defaults({jar: true});

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

///////////////////////////////////////////////////////////////////////////////
// captcha processing

var findCaptchaProcessor = function(item) {
	switch (item.source) {
		case "Libgen":
			return processorLibgen;
		case "Sci-Hub Moscow":
			return processorSciHubMoscow;
		case "Sci-Hub Ocean":
			return processorSciHubOcean;
		case "Sci-Hub Cyber":
			return processorSciHubCyber;
		case "BookSC":
			return processorBookSC;
		case "Torrents":

		default:
			console.error("Unsupported source " + item.source);
			return null;	//identity
	}
}

var processorLibgen = function(url, html, handler) {
	var baseUrl = "";
	var downloadLinkIndex = 1;

	withDownloadLink(html, handler, baseUrl, downloadLinkIndex);
}

var processorSciHubMoscow = function(url, html, outputFile) {
	processorSciHub("moscow", url, html, outputFile);
}

var processorSciHubOcean = function(url, html, outputFile) {
	processorSciHub("ocean", url, html, outputFile);
}

var processorSciHubCyber = function(url, html, outputFile) {
	processorSciHub("cyber", url, html, outputFile);
}

var processorBookSC = function(url, html, outputFile) {
	var baseUrl = "";
	var downloadLinkSelector = "a.ddownload.color2.dnthandler";

	withDownloadLink(html, outputFile, baseUrl, downloadLinkSelector);
}



var processorSciHub = function(subdomain, url, html, outputFile) {
	var baseUrl = "http://" + subdomain + ".sci-hub.bz";
	var postUrl = url;
	var captchaImageSelector = "#captcha";
	var captchaInputName = "captcha_code";

	withCaptchaImageHandler(html, outputFile, baseUrl, postUrl, captchaImageSelector, captchaInputName);
}


var withDownloadLink = function(html, outputFile, baseUrl, downloadLinkSelectorOrIndex) {
	var $ = cheerio.load(html);

	var $download;
	if (isNaN(downloadLinkSelectorOrIndex)) {
		$download = $(downloadLinkSelectorOrIndex);
	} else {
		$download	= $("a").eq(downloadLinkSelectorOrIndex);
	}

	var href = $download.attr("href");
	var url = baseUrl + href;

	downloadFile(url, null, outputFile);
}


var withCaptchaImageHandler = function(html, outputFile, baseUrl, postUrl, captchaImageSelector, captchaInputName) {
	var $ = cheerio.load(html);
	var $captcha = $(captchaImageSelector);
	var src = $captcha.attr("src");
	var url = baseUrl + src;

	console.log("Downloading captcha image " + url);
	var stream = fs.createWriteStream('/tmp/captcha');
	request(url).pipe(stream);
	//TODO open
	
	var readHandler = function(text) {
			var postData = {};
			postData[captchaInputName] = text;
			downloadFile(postUrl, postData, outputFile);
	}
	readFromConsole("Enter captcha code", readHandler);
}

///////////////////////////////////////////////////////////////////////////////
// parsing


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

///////////////////////////////////////////////////////////////////////////////
// download handlers
var processItem = function(item, outputFile) {
	console.log("Downloading '" + item.title + "' by '" + item.author + "' from " + item.source + "\n " + item.url);
	
	var captchaHandler =  function(error, response, body) {
		if (error) {
			console.error("Error #2: " + error);
			return;
		} else {
//		console.log(body);			//XXX testing
			var process = findCaptchaProcessor(item);
			process(item.url, body, outputFile);
		}
	}
	/*
			var stream = fs.createWriteStream('bio');	//XXX testing
	request(item.url).pipe(stream);
	*/

	request.get(item.url, captchaHandler);
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


doTheQuery(query, outputFile, itemIndex, sourceIndex);


