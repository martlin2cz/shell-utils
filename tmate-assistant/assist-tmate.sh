#!/bin/bash
# checks hwthere there's any session to be requtested to be started

TA_HOME_DIR=$HOME/Dropbox/tmate-assistant
TA_TOSTART_DIR=$TA_HOME_DIR/to-start
TA_STARTED_DIR=$TA_HOME_DIR/started
TA_FAILED_DIR=$TA_HOME_DIR/failed
TA_TERMINATED_DIR=$TA_HOME_DIR/terminated
TA_TRASH_DIR=$TA_HOME_DIR/trash

# don't fill if you don't want that stored somewhere on the cloud
TMATE_USERNAME="[USERNAME]"
TMATE_SERVER="lon1.tmate.io"
TMASS_SESSION_NAME_ENV_VAR_NAME="tmate_assistant_session_name"

VERBOSE=""

echo "[Making sure the dropboxed directories exists in $TA_HOME_DIR]"
mkdir -p $TA_TOSTART_DIR
mkdir -p $TA_STARTED_DIR
mkdir -p $TA_FAILED_DIR
mkdir -p $TA_TERMINATED_DIR
mkdir -p $TA_TRASH_DIR

#source $(dirname $BASH_SOURCE)/setenv.sh

###############################################################################
## THAT SESSION
##

address-of-session() {
	local SESSION_NAME=$1
	
	echo "$TMATE_USERNAME/$SESSION_NAME@$TMATE_SERVER"
}

socket-file-of-session() {
	local SESSION_NAME=$1

	echo /tmp/tmate-assistant-$SESSION_NAME.sock
}

current-session-name() {
	local SESSION_NAME=$(tmate display -p '#{'$TMASS_SESSION_NAME_ENV_VAR_NAME'}')
	
	if [ "$SESSION_NAME" == "" ]; then
		echo "[No current session]" >&2
		exit 1
	else
		echo "[Current session name is $SESSION_NAME]" >&2
		echo "$SESSION_NAME"
	fi
}

start-tmate-session() {
	local SESSION_NAME=$1
	
	local ADRESS=$(address-of-session $SESSION_NAME)
	log-message "$SESSION_NAME" "% Starting tmate session on the address $ADRESS"  $TA_TOSTART_DIR $TA_STARTED_DIR

	#TMP_WAIT_TIME=100
	#echo "(FAKE RUNNING $SESSION_NAME, WILL WAIT $TMP_WAIT_TIME sec then)" && sleep $TMP_WAIT_TIME

	#echo $NAME > /tmp/$NAME
	#xed --new-window --wait /tmp/$NAME

	#tmate -n $SESSION_NAME

	local SOCK_FILE=$(socket-file-of-session "$SESSION_NAME")
	tmate -S $SOCK_FILE -n "$SESSION_NAME" new-session -d \
		&& tmate -S $SOCK_FILE set-environment $TMASS_SESSION_NAME_ENV_VAR_NAME $SESSION_NAME \
		&& tmate -S $SOCK_FILE wait tmate-ready 
	
#tmate -hook translate-to-directory $SESSION_NAME "! Terminated $SESSION_NAME session." $TA_STARTED_DIR $TA_TERMINATED_DIR
	return $?
}

terminate-tmate-session() {
	local SESSION_NAME=$1

	log-message "$SESSION_NAME" "! Stopping tmate session $SESSION_NAME" $TA_TERMINATED_DIR
	sleep 1

	local SOCK_FILE=$(socket-file-of-session "$SESSION_NAME")	
	tmate -S $SOCK_FILE kill-session
}

###############################################################################
## SESSION NAME <-> SESSION (LOG) FILE

do-append-another-file-to() {
	local SOURCE_FILE=$1
	local TARGET_FILE=$2
	# echo "[do-append-another-file-to: $SOURCE_FILE | $TARGET_FILE ]" >&2	

	echo "[Found file $SOURCE_FILE, evil twin of $TARGET_FILE joining into that]" 1>&2
	echo "+--  (originally in $SOURCE_FILE)  ---" >> $TARGET_FILE
	sed -e 's/^/| /' $SOURCE_FILE >> $TARGET_FILE
	echo "+-- (end of $SOURCE_FILE) ---" >> $TARGET_FILE
	echo >> $TARGET_FILE
	mv $VERBOSE $SOURCE_FILE --backup=existing $TA_TRASH_DIR
}

export -f do-append-another-file-to
export TA_TRASH_DIR

file-of-session-name() {
	local SESSION_NAME=$1
	local STATUS_DIRECTORY=$2
	
	local FILE_NAME=$SESSION_NAME".txt"
	local TARGET_FILE=$STATUS_DIRECTORY"/"$FILE_NAME

	# echo "[file-of-session-name: $SESSION_NAME | $STATUS_DIRECTORY | $FILE_NAME | $TARGET_FILE ]" >&2

	find $TA_TOSTART_DIR $TA_STARTED_DIR $TA_TERMINATED_DIR $TA_FAILED_DIR \
		-name $FILE_NAME ! -wholename $TARGET_FILE \
		-exec bash -c 'do-append-another-file-to $0 $1' {} $TARGET_FILE \;

	echo $TARGET_FILE
}

session-name-of-file() {
	local FILE=$1
	
	local FILENAME=$(basename $FILE)	
	local SESSION_NAME=${FILENAME%%.*}
	
	# echo "[session-name-of-file: $FILE | $FILENAME | $SESSION_NAME ]"

	echo "$SESSION_NAME"
}

###############################################################################

log-message() {
	local SESSION_NAME=$1
	local MESSAGE=$2
	local STATUS_DIRECTORY=$3
	local FILE=$(file-of-session-name "$SESSION_NAME" $STATUS_DIRECTORY)
	
	# echo "[log-message: $SESSION_NAME | $MESSAGE | $STATUS_DIRECTORY | $FILE]" >&2

	date >> $FILE
	echo "$MESSAGE" | tee -a $FILE
	echo >> $FILE
}

translate-to-directory() {
	local SESSION_NAME=$1
	local MESSAGE=$2
	local CURRENT_DIR=$3
	local DESTINATION_DIR=$4
	
	# echo "[translate-to-directory: $SESSION_NAME | $MESSAGE | $CURRENT_DIR | $DESTIONATION_DIR]" >&2

	# log the message
	log-message "$SESSION_NAME" "$MESSAGE" $CURRENT_DIR 

	# compute the source and target file
	SOURCE_FILE=$(file-of-session-name $SESSION_NAME $CURRENT_DIR)
	FILENAME=$(basename $SOURCE_FILE)
	MOVED_FILE=$DESTINATION_DIR"/"$FILENAME

	# actually move thefile	
	mv $VERBOSE $SOURCE_FILE $MOVED_FILE
	
	# indicate the status of the logfile
	log-message "$SESSION_NAME" "<Translated (moved) $SESSION_NAME from $CURRENT_DIR to $DESTINATION_DIR>" $DESTINATION_DIR 
}

###############################################################################

do-backup-non-txt-session-file() {
	local SESSION_NAME=$1
	local NONTXT_FILE=$2

	echo "[Found $NONTXT_FILE, moving to trash and constructing txt file instead]" 1>&2
	FILE_NAME=$(basename $NONTXT_FILE)
	TRASHED_FILE=$TA_TRASH_DIR"/"$FILE_NAME
	mv $VERBOSE --backup=existing $NONTXT_FILE $TRASHED_FILE

	FILE_WITH_TXT=$SESSION_NAME".txt"
	FILE=$FILE_WITH_TXT
	echo "<Creating file as replacement of the $FILE>" >> $FILE_WITH_TXT
}

list-session-names-in() {
	local DIR=$1	

	for FILE in $(find $DIR -type f); do

		SESSION_NAME=$(session-name-of-file $FILE)

		if [ ${FILE##*.} != "txt" ] ; then
			do-backup-non-txt-session-file "$SESSION_NAME" $FILE
		fi

		echo "$SESSION_NAME"
	done
}

###############################################################################


unit-tests() {
	IN_FILE=$TA_TOSTART_DIR/foo.xml
	
	echo "<whatever/>" > $IN_FILE
	echo "User created file $IN_FILE"

	echo "== (session-tofile-test) =========================="
	SESSION_NAME=$(session-name-of-file $TA_TOSTART_DIR/foo.xml)
	echo "(session-tofile test) ... which translates to $SESSION_NAME"

	echo "== (file-of-session-name) =========================="	
	echo "Sun rays created $TA_FAILED_DIR/foo.txt too to introduce evil twin"
	echo "whatever else fakelly failed" > $TA_FAILED_DIR/foo.txt
	FILE=$(file-of-session-name $SESSION_NAME $TA_TOSTART_DIR)
	echo "== (file-of-session test) ... which reports to $FILE:"
	cat $FILE

	echo "== (log-message) =========================="
	log-message $SESSION_NAME "(logging test) Somthing is happening..." $TA_TOSTART_DIR
	echo "The file contains now:"
	cat $FILE
	echo "== (log-message) logged ===================="

	echo "== (session-tofile-test) =========================="
	translate-to-directory $SESSION_NAME "(translate test) And it's actually almost done!" $TA_TOSTART_DIR $TA_STARTED_DIR
	STARTED_FILE=$TA_STARTED_DIR/foo.txt
	cat $STARTED_FILE
	echo "== (session-tofile-test) translated ==============="
	
	echo "== (list-session-names-in) listing ==============="
	echo "Creating foo.foc, BAR.JPEG and baz.md in $TA_TOSTART_DIR"
	echo "This is Foo.doc" > $TA_TOSTART_DIR/foo.doc
	echo "THIS IS BAR.JPEG" > $TA_TOSTART_DIR/BAR.JPEG
	echo "this is baz.md" > $TA_TOSTART_DIR/baz.md
	
	list-session-names-in $TA_TOSTART_DIR
	echo "== (list-session-names-in) listed ==============="
	

}

usual-use-case-test() {
	INFILE=$TA_TOSTART_DIR/lorem.xml
	echo "<whatever-else />" > $INFILE 
	echo "User created file $INFILE"

	SESSION_NAME=$(session-name-of-file $INFILE)	
	translate-to-directory $SESSION_NAME "(testing) Started!" $TA_TOSTART_DIR $TA_STARTED_DIR
	translate-to-directory $SESSION_NAME "(testing) Terminated!" $TA_STARTED_DIR $TA_TERMINATED_DIR
	translate-to-directory $SESSION_NAME "(testing) Failed!" $TA_TERMINATED_DIR $TA_FAILED_DIR

	OUTFILE=$TA_FAILED_DIR/$SESSION_NAME.txt
	echo "== resulting file: ==="
	cat $OUTFILE
	echo "== eof resulting file ==="
}

integration-tests() {
	echo "=== (list-all) executing ====="
	echo "Creating karel.md, franta.txt, pepa.txt and lojza.txt"
	touch $TA_TOSTART_DIR/karel.md
	touch $TA_STARTED_DIR/franta.txt
	touch $TA_STARTED_DIR/pepa.txt
	touch $TA_TERMINATED_DIR/lojza.txt
	list-all
	echo "=== (list-all) done ====="
}

run-test() {
	unit-tests
	usual-use-case-test

	integration-tests
}

###############################################################################

check-and-start-session() {
	local SESSION_NAME=$1

	if ! [[ $SESSION_NAME =~ [a-zA-Z0-9]+ ]]; then
		translate-to-directory $SESSION_NAME "! The '$SESSION_NAME' doesn't match the allowed session name, skipping." $TA_TOSTART_DIR $TA_FAILED_DIR
		continue
	fi

	log-message $SESSION_NAME "! Starting $SESSION_NAME session ..." $TA_TOSTART_DIR

	start-tmate-session $SESSION_NAME
	STARTED=$?
	if [ "$STARTED" -eq 0 ] ; then
		translate-to-directory $SESSION_NAME "! Started $SESSION_NAME session." $TA_TOSTART_DIR $TA_STARTED_DIR
	else
		translate-to-directory $SESSION_NAME "! Failed start of $SESSION_NAME session." $TA_TOSTART_DIR $TA_FAILED_DIR 
	fi
}

check-and-start-sessions() {
	echo "# Checking sessions to start from $TA_TOSTART_DIR ..."
	for SESSION_NAME in $(list-session-names-in $TA_TOSTART_DIR) ; do
		check-and-start-session $SESSION_NAME
	done
	echo "# Checked sessions to start."
}

start-manually() {
	local SESSION_NAME=$1

	INITIAL_FILE=$TA_TOSTART_DIR/$SESSION_NAME.txt
	echo "[Creating $INITIAL_FILE]" >&2
	touch $INITIAL_FILE
	log-message $SESSION_NAME "Manually created file $INITIAL_FILE for the session named $SESSION_NAME." $TA_TOSTART_DIR

	check-and-start-session $SESSION_NAME
}

terminate-session() {
	local SESSION_NAME=$1
	
	# we have to translate first, the process gets terminated by the session termination
	translate-to-directory $SESSION_NAME "! Session $SESSION_NAME will be terminated." $TA_STARTED_DIR $TA_TERMINATED_DIR

	terminate-tmate-session $SESSION_NAME

	log-message $SESSION_NAME "! Session $SESSION_NAME terminated." $TA_TERMINATED_DIR
}

list-all() {
	
	echo "== Sessions to start ( $TA_TOSTART_DIR ):"
	list-session-names-in $TA_TOSTART_DIR
	echo

	echo "== Sessions started ( $TA_STARTED_DIR ):"
	list-session-names-in $TA_STARTED_DIR
	echo

	echo "== Sessions terminated ( $TA_TERMINATED_DIR ):"
	list-session-names-in $TA_TERMINATED_DIR
	echo

	echo "== Sessions failed ( $TA_FAILED_DIR ):"
	list-session-names-in $TA_FAILED_DIR
	echo
}

if [ "$1" == "-v" ] || [ "$1" == "--verbose" ] ; then
	echo "[Verbose mode on]" >&2
	VERBOSE="--verbose"
	shift
fi

case $1 in
	"check" | "start" | "check-and-start")
		check-and-start-sessions
	;;
	"start-manually" | "start-now")
		if [ "$2" == "" ]; then
			echo "Missing session name" >&2
			exit 2
		fi
		start-manually $2
	;;
	"die" | "kill" | "terminate")
		SESSION_NAME=
		if [ "$2" == "" ]; then
			SESSION_NAME=$(current-session-name)
			if [ "$SESSON_NAME" == "" ]; then
				echo "No curent session." >&2
				exit 3
			fi
		else
			SESSION_NAME=$2
		fi
		terminate-session $SESSION_NAME
	;;
	"status")
		echo "Current session: " $(current-session-name)
		list-all
	;;
	"print" | "list")
		list-all
	;;
	"test")
		run-test
	;;
	*)
		echo "$0 v1.1"
		echo "Usage: $0 COMMAND [ARGS]"
		echo "check|start|check-and-start		Checks for all sessions to-start and starts them"
		echo "start-manually|start-now SESSION_NAME	Starts the specifcied session immediatelly"
		echo "die|kill|terminate [SESSION_NAME]		Terminates the given or current session"
		echo "status					Prints information about the current and other sessions"
		echo "print|list				List all the sessions"
	;;

esac
