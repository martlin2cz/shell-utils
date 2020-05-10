// open dev tools by Ctrl+Shift+I and:

/////////////////////////////////////////////////////////////////////

function findPanelsContainer() {
	return document
		.querySelector('body > main-view').shadowRoot
		.querySelector('section > section > history-page').shadowRoot
		.querySelector('section > opr-main > opr-content');
}

function findPanels(panelsContainer) {
	return panelsContainer.querySelectorAll('opr-panel');	
}

function findEntriesGroups(panel) {
	return panel.querySelectorAll('ol > div');	
}

function findPanelGroupsContainer(panel) {
	return panel.querySelector('ol');
}

function findEntries(group) {
	return group.querySelectorAll('a.visit-entry');
}

function findLoader() {
	return document
		.querySelector('body > main-view').shadowRoot
		.querySelector('section > section > history-page')
		.shadowRoot.querySelector('#loader')
}

function panelOfEntry(entry) {
	return entry.parentElement.parentElement.parentElement
}

function isPanel(node) {
	return (node.nodeName == 'OPR-PANEL');
}

function isGroup(node) {
	return (node.nodeName == 'DIV');
}

/////////////////////////////////////////////////////////////////////

function dateFromPanel(panel) {
	return panel.shadowRoot
		.querySelector('main > h2').firstChild.nodeValue;
}

function dataFromEntry(entry) {
	const url = entry.getAttribute("href");
	const time = entry.querySelector('.visit-time').firstChild.nodeValue;
	const server = entry.querySelector('.visit-url').firstChild.nodeValue;
	const title = entry.querySelector('.visit-title').firstChild.nodeValue;
	const favicons = entry.querySelector('.visit-favicon').style.backgroundImage;

	return { "url": url, "time": time, "server": server, "title": title, "favicons": favicons};
}

function completeDataFromEntry(entry) {
	var data = dataFromEntry(entry);
	
	const panel = panelOfEntry(entry);

	dateSpec = dateFromPanel(panel);
	data['date_spec'] = dateSpec;
	return data;
}

/////////////////////////////////////////////////////////////////////

function handleNewPanel(panel) {
	console.log(dateFromPanel(panel));
}

function listAdded(mutations) {
	var result = [];

	mutations.forEach((mutation) => {
		mutation.addedNodes.forEach((addedNode) => {
			result.push(addedNode);
		});
	});

	return result;
}

/////////////////////////////////////////////////////////////////////
HANDLE_TIMEOUT = 10 * 1000;
SCROLL_TIMEOUT = 10 * 1000;

function doit() {
	const callback = function(mutations, observer) {
		handleMutations(mutations, observer);		
	};

	const observer = prepareTheObserver(callback);
	const container = findPanelsContainer();
	startObserving(container, observer);

	const panels = findPanels(container);
	for (panel of panels) {
		handlePanel(panel, observer);
	}

	//scrollDown();	
	console.info("Okay, running!");
	
}

function prepareTheObserver(callback) {
	const observer = new MutationObserver(callback);
	return observer;
}

function startObserving(node, observer) {
	const config = { childList: true }
	observer.observe(node, config);
}

function scrollDown() {
	//console.log("Scrolling down")
	loader = findLoader();
	loader.scrollIntoView();	
}
/*	
window.setTimeout(function() {
			handleMutations(mutations, observer);

			window.setTimeout(function() {
				scrollDown();
			}, SCROLL_TIMEOUT);
		}, HANDLE_TIMEOUT);
*/



function handleMutations(mutations, observer) {
	addeds = listAdded(mutations);
	
	window.setTimeout(function() {
		handleAddeds(addeds, observer);
	}, HANDLE_TIMEOUT);
	
	//window.setTimeout(function() {
	//	scrollDown();
	//}, SCROLL_TIMEOUT);
}


function handleAddeds(addeds, observer) {
	for (added of addeds) {
		//console.debug(added);
		if (isPanel(added)) {
			handlePanel(added, observer);
		}
		if (isGroup(added)) {
			handleGroup(added);
		}
	}
}

function handlePanel(panel, observer) {
	const panelContainer = findPanelGroupsContainer(panel);
	startObserving(panelContainer, observer);	
}

function handleGroup(group) {
	for (entry of findEntries(group)) {
		data = completeDataFromEntry(entry);
		sendEntryData(data);
		console.log("Reported entry");
	}
}


function sendEntryData(data) {
	//console.log("Reporting entry " + data);
	req = new XMLHttpRequest()
	req.open("POST", "http://localhost:8082/add")
	req.setRequestHeader("Content-Type", "application/json");
	
	const json = JSON.stringify(data);
	req.send(json);
}

doit();

/*
panelsContainer = findPanelsContainer();

panels = findPanels(panelsContainer); 

date = dateFromPanel(panels[0]);

groups = findEntriesGroups(panels[0]);

entries = findEntries(groups[0]);

data = dataFromEntry(entries[0]);
*/

