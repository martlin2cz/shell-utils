/**
 * An nodejs service which listens on localhost:PORT/add
 * for json data to be inserted into sqlite database DB_FILE.
 * */

///////////////////////////////////////////////////////////////////////////////

const sqlite3 = require("sqlite3")
const express = require('express');
const ws = express();

///////////////////////////////////////////////////////////////////////////////
// the port where the service runs on
const PORT = 8082;

// the database file where to store the collected data
const DB_FILE = process.argv.slice(2)[0];

///////////////////////////////////////////////////////////////////////////////


function dbConnect() {
	const db = new sqlite3.Database(DB_FILE);
	console.info("database created");
	return db;
}

function dbCreateTable(db) {
	const sql = "CREATE TABLE IF NOT EXISTS history"
	+ "(date TEXT, time TEXT, server TEXT, url TEXT, title TEXT)";

	db.run(sql);
	console.info("table created");
}

function dbInsert(db, entry) {
	const sql = "INSERT INTO history" 
		+ " (date, time, server, url, title)"
		+ " VALUES (?,?,?,?,?)";
	const values =[entry.date, entry.time, entry.server, entry.url, entry.title];
	db.run(sql, values);

	//console.info("inserted " + JSON.stringify(entry));
	process.stdout.write(".");
}

function dbInserts(db, entries) {
	const sql = "INSERT INTO history" 
		+ " (date, time, server, url, title)"
		+ " VALUES "
		+ entries.map((e) => "(?,?,?,?,?)").join(", ");
	
	var values = [];
	for (entry of entries) {
		const entryValues = [entry.date, entry.time, entry.server, entry.url, entry.title];
		values.push(...entryValues);
	}

	db.run(sql, values);
	//console.info("inserted " + JSON.stringify(entries));
	process.stdout.write("o");
}

function dbDisconnect(db) {
	db.close();
	console.info("database disconected");
}

///////////////////////////////////////////////////////////////////////////////

function wsStart(oneHandler, moreHandler) {
	ws.use(express.json({
		extended: true,
		limit: '10mb'
	}));
	ws.use(express.urlencoded({
		extended: false,
		limit: '10mb'

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
		oneHandler(entry);
	
		res.header("Access-Control-Allow-Origin", "*"); 
		res.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
		res.end("ok");
	})

	ws.post('/adds', function (req, res) {
		const entries = req.body
		moreHandler(entries);
	
		res.header("Access-Control-Allow-Origin", "*"); 
		res.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
		res.end("oks");
	})

	const server = ws.listen(PORT, function () {
		console.info("Service running")
	});

	return server;
}

function wsStop(server) {
	server.close(function () {
		console.info("Service stopped");
	});
}


///////////////////////////////////////////////////////////////////////////////

console.info("Starting the collecter service");

const db = dbConnect();
dbCreateTable(db);

const oneHandler = function(entry) {
	dbInsert(db, entry);
}

const moreHandler = function(entries) {
	dbInserts(db, entries);
}


const server = wsStart(oneHandler, moreHandler);

const interrupter = function() {
	console.info("Terminating the collecter service");

	dbDisconnect(db);
	wsStop(server);
}

process.on('SIGINT', interrupter);

