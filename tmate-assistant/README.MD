# tmate-assistant

A tool for automatic starting of named tmate sessions, based on the specification uploaded into a Dropbox (or, potenticnally any other cloud service) folder, based on the `tmate` tool.

## Basic idea:
	1. Have _$TA_HOME_DIR_ directory ready (existing and pointing to the shared, cloud accesible directory)
	2. To deploy as a service, execute the `./deploy.sh` script, otherwise you have to do the check for new session requests manually
	3. From a remote location, upload a file into the _$TA_HOME_DIR/to-start_ directory (with the name (ignoring the extension) matching the desired name of the session)
	4. To execute manually run (or let the systemd to run it automatically): `./assist-tmate.sh check-for-start`
	5. If suceeds, appropriet session will get started and the "session name" file will get moved into the _started_ directory and outputs the credentials into the file
	6. If not, "session name" file will get moved to _failed_ directory, again, containing explanation of the failure (if any)
	7. -Once the session got terminated, the "session name" file will get moved to _terminated_ folder- (not possible due BUG? in the tmate)
	8. If you are done with your work, run `./assist-tmate.sh terminate` (from within your session) or `./assist-tmate.sh terminate SESSION_NAME` (from either inside or outside) to close the tmate session and move the "session name" file to _$TA_HOME_DIR/terminated_ .

## Furthermore:
	- run `./assist-tmate.sh print` to see current status
	- run `./assist-tmate.sh start-manually SESSION_NAME` to start that session as if it was triggered by the "session name" file and the `check-and-start`
	- the "session name" file should be _*.txt_ file, but any other file than that will get replaced (original file will get moved to _trash_ directory and a new, empty text file will get created instead) by a same-named _*.txt_ file
	- run `./deploy.sh` to install as a systemd timer service (otherwise you have to start the sessions manually, which actually makes this whole tool kinda useless)
	

## Main idea:
The main goal is the timer. The timer checks (polls) twice an hour (during the week) and twice the day for the session to start, and if found some, starts them. Therefore, you can ping the server to open new tmate session by just uploading a file to a shared location (cloud) and wait less then hour to get started and you have your session running. The filename of the file you uploaded indicates the name of the session, the credentials gets outputted into the session name file.


