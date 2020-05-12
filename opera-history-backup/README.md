# the opera-history-exporter

Quite crazy way, how to export the opera (or, maybe, generally chromium based web browser) history. Cannot be simply automatised, hence needs a bit of user assistance. Run the `runit.sh` and follow the instructions.

tl;dr the source:

 - open the browser and history page
 - let to be scrolled down (by the script) as much as desired (remember, browser keeps the history only last three months)
 - let the nodejs service to be started
 - copy the javascript code
 - execute the javascript code inside of the history page
 - let the javascript in the browser to collect the history entries and send them to nodejs service
 - the service outputs them to the sqllite3 database
 - finally, verify and terminate the service


