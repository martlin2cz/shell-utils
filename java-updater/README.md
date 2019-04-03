# java-updater

Simple script for automated reinstallation of java in system. Usefull when you want to have the latest java (jdk) installed, but your package manager does not support that.

## Usage:
Download and extract java (jdk) to current directory subdir. Then run java-updater. It will `update alternatives` its programs (which ones is specified in the script itself) to priority YYMM where YY is current year and MM is current month (i.e. 1904). This will assume that each next update (excluding one installed in the same month, obviously) will has higher priority than the previous one.

````
    $ su
    # cd SOMEWHERE
    # unzip THE_JDK_VERSION_X.zip -d .
    # ls .
    the-jdk-version-x/ the-jdk-version-y/
    # ./update-java the-jdk-version-x/
    Installing the-jdk-version-x/ with priority 1904 ...
    Installing java ...
    Installing javac ...
    Installing javadoc ...
    Installing jmap ...
    Installed, see:
    somejdk version "X" somebuild
    # 
````
