
const sqlite3 = require("sqlite3")
const express = require('express');
const ws = express();
//const bodyParser = require('body-parser');


const DB_FILE = "history.db";

function dbConnect() {
	const db = new sqlite3.Database(DB_FILE);
	console.info("database created");
	return db;
}

function dbCreateTable(db) {
	const sql = "CREATE TABLE history"
	+ "(date_spec TEXT, time TEXT, server TEXT, url TEXT, title TEXT, favicons TEXT)";

	db.run(sql);
	console.info("table created");
}

function dbInsert(db, entry) {
	const sql = "INSERT INTO history" 
		+ " (date_spec, time, server, url, title, favicons)"
		+ " VALUES (?,?,?,?,?,?)";
	const values =[entry.date_spec, entry.time, entry.server, entry.url, entry.title, entry.favicons];
	db.run(sql, values);
	//console.info("inserted " + JSON.stringify(entry));
}

function dbDisconnect(db) {
	db.close();
	console.info("database disconected");
}

/////
function wsStart(handler) {
	ws.use(express.json());
	ws.use(express.urlencoded({
		  extended: false
	}));

	ws.all("/*", function (req, res, next) {
		res.header("Access-Control-Allow-Origin", "*");
		res.header("Access-Control-Allow-Credentials",true);
		res.header('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS');
		res.header('Access-Control-Allow-Headers', 'Content-Type,Accept,X-Access-Token,X-Key,Authorization,X-Requested-With,Origin,Access-Control-Allow-Origin,Access-Control-Allow-Credentials');
		
		if (req.method === 'OPTIONS') {
			res.status(200).end();
		} else {
			next();
		}
	});

	ws.post('/add', function (req, res) {
		//console.log(req.headers);
		//console.log(req.body);
		const entry = req.body
		handler(entry);
	
		res.header("Access-Control-Allow-Origin", "*"); 
		res.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
		res.end("ok");
	})

	const server = ws.listen(8082, function () {
		var host = server.address().address
		var port = server.address().port
		console.info("Service listening at http://%s:%s", host, port)
	});
}

//#TODO stop server

////////

const db = dbConnect();
dbCreateTable(db);

const handler = function(entry) {
	dbInsert(db, entry);
}

wsStart(handler);

