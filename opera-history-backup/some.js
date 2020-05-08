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
	const time = entry.querySelector('.visit-time').firstChild.nodeValue;
	const url = entry.querySelector('.visit-url').firstChild.nodeValue;
	const title = entry.querySelector('.visit-title').firstChild.nodeValue;

	return { "time": time, "url": url, "title": title };
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


function doit() {
	const callback = function(mutations, observer) {
		for (added of listAdded(mutations)) {
			console.debug(added);
			if (isPanel(added)) {
				handlePanel(added, observer);
			}
			if (isGroup(added)) {
				handleGroup(added);
			}
		}
	};

	const observer = prepareTheObserver(callback);
	const container = findPanelsContainer();
	startObserving(container, observer);

	const panels = findPanels(container);
	for (panel of panels) {
		handlePanel(panel, observer);
	}
	
}

function handlePanel(panel, observer) {
	const panelContainer = findPanelGroupsContainer(panel);
	startObserving(panelContainer, observer);	
	//TODO scroll down
}

function handleGroup(group) {
	console.log("Handling group");
	
	for (entry of findEntries(group)) {
		data = completeDataFromEntry(entry);
		console.log(data);
	}
}



function prepareTheObserver(callback) {
	const observer = new MutationObserver(callback);
	return observer;
}

function startObserving(node, observer) {
	const config = { childList: true }
	observer.observe(node, config);
}

/*
panelsContainer = findPanelsContainer();

panels = findPanels(panelsContainer); 

date = dateFromPanel(panels[0]);

groups = findEntriesGroups(panels[0]);

entries = findEntries(groups[0]);

data = dataFromEntry(entries[0]);
*/

