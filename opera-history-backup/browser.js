/* The browser script.
 * Collects all the history entries from the history page and sends to nodejs server.
 * */

////////////////////////////////////////////////////////////////////////////

/**
 * The port where the consuming service is listening.
 * */
const SERVICE_PORT = 8082;

////////////////////////////////////////////////////////////////////////////

/**
 * Returns the container with the panels.
 * */
function findPanelsContainer() {
	return document
		.querySelector('body > main-view').shadowRoot
		.querySelector('section > section > history-page').shadowRoot
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
	return panel.shadowRoot
		.querySelector('main > h2').firstChild.nodeValue;
}

/**
 * Extracts the url, time, server, title and favicons values from the given entry.
 * */
function dataFromEntry(entry) {
	const url = entry.getAttribute("href");
	const time = entry.querySelector('.visit-time').firstChild.nodeValue;
	const server = entry.querySelector('.visit-url').firstChild.nodeValue;
	const title = entry.querySelector('.visit-title').firstChild.nodeValue;
	const favicons = entry.querySelector('.visit-favicon').style.backgroundImage;

	return { "url": url, "time": time, "server": server, "title": title, "favicons": favicons};
}

/**
 * Collects complete data for the given entry.
 * */
function completeDataFromEntry(entry) {
	var data = dataFromEntry(entry);
	
	const panel = panelOfEntry(entry);

	dateSpec = dateFromPanel(panel);
	data['date_spec'] = dateSpec;
	return data;
}

////////////////////////////////////////////////////////////////////////////

/**
 * Runs the report of all the entries in all groups in all panels.
 * */
function reportAll() {
	console.log("Reporting. To re-run type 'reportAll()'.");
	const panelsContainer = findPanelsContainer();
	
	const panels = findPanels(panelsContainer); 
	for (panel of panels) {
		const groups = findEntriesGroups(panel);
		for (group of groups) {
			const entries = findEntries(group);
			for (entry of entries) {
				processEntry(entry);
			}
		}
	}
	
	console.log("Reported");
}

/**
 * Processes the given entry. Collects data and sends them.
 * */
function processEntry(entry) {
	data = completeDataFromEntry(entry);
	sendEntryData(data);
	console.log("Reported entry");
}


/**
 * Sends the given data to server.
 * */
function sendEntryData(data) {
	//console.log("Reporting entry " + data);
	const req = new XMLHttpRequest();
	const url = "http://localhost:" + SERVICE_PORT + "/add";

	req.open("POST", url, false);
	req.setRequestHeader("Content-Type", "application/json");
	
	const json = JSON.stringify(data);
	req.send(json);
}


////////////////////////////////////////////////////////////////////////////

/*
 * Runs the reporting itself.
 */
reportAll();
