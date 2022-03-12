/* The browser script.
 * Collects all the history entries from the history page and sends to nodejs server.
 * */

////////////////////////////////////////////////////////////////////////////

/**
 * The port where the consuming service is listening.
 * */
const SERVICE_PORT = 8082;

/**
 * The size of the batch to be reported.
 * */
const GROUP_SIZE = 20;


////////////////////////////////////////////////////////////////////////////

/**
 * Returns the container with the panels.
 * */
function findPanelsContainer() {
//	return document
//		.querySelector('body > main-view').shadowRoot
//		.querySelector('section > section > history-page').shadowRoot
//		.querySelector('section > opr-main > opr-content');
	return document.querySelector('body > main-view').shadowRoot
		.querySelector('section > history-page ').shadowRoot
		.querySelector('section > opr-main > opr-content');
}

/**
 * Returns the list of panels of the given panels container.
 * */
function findPanels(panelsContainer) {
	return panelsContainer.querySelectorAll('opr-panel');	
}

/**
 * Returns the groups of entries of given panel.
 * */
function findEntriesGroups(panel) {
	return panel.querySelectorAll('ol > div');	
}

/**
 * Returns the entries of the given group of entries.
 * */
function findEntries(group) {
	return group.querySelectorAll('a.visit-entry');
}

/**
 * Returns (back to top) the panel owning the given entry.
 * */
function panelOfEntry(entry) {
	return entry.parentElement.parentElement.parentElement
}

////////////////////////////////////////////////////////////////////////////

/**
 * Extract the 'date_spec' value from the given panel.
 * */
function dateFromPanel(panel) {
	const dateSpec = panel.shadowRoot
		.querySelector('main > h2').firstChild.nodeValue;
	
	//                              Today -    Sunday     ,   March         12     ,    2022       
	var matches = dateSpec.match("^([^ ]+ - )?([A-Z][a-z]+\, [A-Z][a-z]+ [0-9]{1,2}\, [0-9]{4})$");
	return matches.length == 4 ? matches[3] : matches[2];
}

/**
 * Extracts the url, time, server, title and favicons values from the given entry.
 * */
function dataFromEntry(entry) {
	const url = entry.getAttribute("href");
	const time = entry.querySelector('.visit-time').firstChild.nodeValue;
	const server = entry.querySelector('.visit-url').firstChild.nodeValue;
	const title = entry.querySelector('.visit-title').firstChild.nodeValue;

	return { "url": url, "time": time, "server": server, "title": title };
}

/**
 * Collects complete data for the given entry.
 * */
function completeDataFromEntry(entry) {
	var data = dataFromEntry(entry);
	
	const panel = panelOfEntry(entry);

	date = dateFromPanel(panel);
	data['date'] = date;
	return data;
}

////////////////////////////////////////////////////////////////////////////

/**
 * Runs the report of all the entries in all groups in all panels.
 * */
function reportAll() {
	// console.log(new Date());
	console.log("Reporting started. To re-run type 'reportAll()'.");
	
	const elements = collectEntriesElements();
	const datas = collectEntriesDatas(elements);
	reportTheEntriesDatas(datas);
	
	// console.log(new Date());
	console.log("Reporting done.");
}

/**
 * Lists all the entry elements.
 * */
function collectEntriesElements() {
	console.log("collecting the entries elements ...");

	var result = [];
	const panelsContainer = findPanelsContainer();
	
	const panels = findPanels(panelsContainer); 
	for (panel of panels) {
		const groups = findEntriesGroups(panel);
		for (group of groups) {
			const entries = findEntries(group);
			for (entry of entries) {
				result.push(entry);
			}
		}
	}

	return result;
}

/**
 * For each entry element obtains its data.
 * */
function collectEntriesDatas(entries) {
	return entries.map((entry) => 
		completeDataFromEntry(entry));
}

/**
 * Runs the reporting of the given entries datas.
 * If GROUP_SIZE is bigger than one, reports by groups,
 * otherwise one by one.
 * */
function reportTheEntriesDatas(entries) {
	if (GROUP_SIZE <= 1) {
		console.log("reporting " + datas.length + " of entries ...");
		for (entry of entries) {
			reportEntryData(entry);
		}
	
	} else {
		const groups = groupify(entries);
		console.log("reporting " + groups.length + " of groups ...");
		for (group of groups) {
			reportEntriesDatas(group);
		}
	}
}

/**
 * Splits the given array to groups of GROUP_SIZE size.
 * */
function groupify(entries) {
	var gsi;
	var result = [];
	for (gsi = 0; true; gsi += GROUP_SIZE) {
		const group = entries.slice(gsi, gsi + GROUP_SIZE);
		
		if (group.length > 0) {
			result.push(group);
		} else {
			break;
		}
	}

	return result;
}

/**
 * Sends the given entry data to server.
 * */
function reportEntryData(data) {
	try {
		const req = new XMLHttpRequest();
		const url = "http://localhost:" + SERVICE_PORT + "/add";

		req.open("POST", url, false);
		req.setRequestHeader("Content-Type", "application/json");
	
		const json = JSON.stringify(data);
		req.send(json);

		console.info("reported entry data");
	} catch (ex) {
		console.error(ex);
		console.warn(data);
	}
}

/**
 * Sends the given entry data to server.
 * */
function reportEntriesDatas(datas) {
	try {
		const req = new XMLHttpRequest();
		const url = "http://localhost:" + SERVICE_PORT + "/adds";

		req.open("POST", url, false);
		req.setRequestHeader("Content-Type", "application/json");
	
		const json = JSON.stringify(datas);
		req.send(json);

		console.info("reported group of " + GROUP_SIZE + " entries of datas");
	} catch (ex) {
		console.error(ex);
		console.warn(datas);
	}
}

////////////////////////////////////////////////////////////////////////////

/*
 * Runs the reporting itself.
 */
reportAll();
