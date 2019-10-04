@echo off
REM Copies all contents from CD to specified location
REM m@rtlin, 2.12.2018

:: #######################################

:: the source (the cd) (without the leading \, please)
SET FROM=D:

:: the target (the external, or internal drive, and its sub-folder) (without the leading \, please)
SET TO=E:\janca\audioknihy

:: the readme file name
SET READMENAME=cojeto.txt

:: ######################################

:: check the input
IF [%1]==[] (
	ECHO "Použití: %0 '<AUTOR>' '<nazev>'"
	PAUSE
	EXIT
)
IF [%2]==[] (
	ECHO "Použití: %0 '<autor>' '<NAZEV>'"
	PAUSE
	EXIT
)

:: name of the author of the content
SET AUTHOR=%~1

:: title of the cotent
SET TITLE=%~2

:: ######################################

:: construct dirname for the target
SET DIRNAME=%AUTHOR% - %TITLE%

:: create target dir
SET TARGET=%TO%\%DIRNAME%
MKDIR "%TARGET%"

:: do the copy
SET SOURCE=%FROM%\
ROBOCOPY %SOURCE% "%TARGET%"

:: create the readme file
SET READMEFILE=%TARGET%/%READMENAME%
echo "AUTOR: %AUTHOR%" > "%READMEFILE%"
echo "TITUL: %TITLE%" >> "%READMEFILE%"
echo "ZDROJ: K. M. P." >> "%READMEFILE%"



:: okay?
ECHO Zkopírováno do %DIRNAME% !
eject.vbs

::PAUSE
EXIT
