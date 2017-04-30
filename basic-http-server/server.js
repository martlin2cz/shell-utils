var http = require('http');

var PORT = 8000;

var stringifyRecursive = function(obj) {
	//http://stackoverflow.com/questions/11616630/json-stringify-avoid-typeerror-converting-circular-structure-to-json
	var cache = [];
	var text = JSON.stringify(obj, function(key, value) {
    if (typeof value === 'object' && value !== null) {
        if (cache.indexOf(value) !== -1) {
            // Circular reference found, discard key
            return "[object]";
        }
        // Store value in our collection
        cache.push(value);
    }
    return value;
	}, 2);
	
cache = null;


	return text;

}

var handleRequest = function(req, res) {
	res.writeHead(200, {'Content-Type': 'text/plain'});
 
	var text = stringifyRecursive(req); 
	console.log(text);
	res.end(text);
}

http //
	.createServer(handleRequest) //
	.listen(PORT); //

console.log("Server ready at port " + PORT);
