@echo off
REM does the copy, but prompts interactivelly for the input

CLS
ECHO Tento programek zkopiruje obsah CD na externi disk
ECHO Po dokonceni se disk automaticky vysune a toto okno se zavre
ECHO Zadej udaje o audioknizce v CD mechanice:
ECHO (nejlepe bez diakritiky)
ECHO 

SET /p AUTHOR=Autor: 
SET /p TITLE=Nazev: 
SET /p DISKNO=CD cislo ... 

ECHO 
ECHO Jsou uveden udaje OK? Je vlozeno CD (D:) a pripojen externi disk (E:)? 
ECHO Pokud ne, toto okno zavrete, pokud ano, pokracujte
ECHO 
PAUSE

CALL copy.BAT "%AUTHOR%" "%TITLE%" "%DISKNO"