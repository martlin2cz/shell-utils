#!/bin/bash
#Zde je název textového editoru - vim, vi, nano, ... (výchozí je vim) 
editor="vim"

parser() { #rozdělá adresu na složku a soubor
	cesta=$(echo $1 | sed -r 's:/:/:' | sed -r 's:(^[^~/]):'$(pwd)'/\1:' | sed -r 's:~:'$HOME':')
	slozka=$(echo $cesta | sed -r 's:(.*)/(.*):\1:')
        xsoubor=$(echo $cesta | sed -r 's:(.*)/(.*):\2:')
	soubor=$(echo $xsoubor | sed -r 's:\.c$::i')
	if [ "$soubor" = "" ]; then
		zdrojak=""
	else
		zdrojak=$soubor".c"
	fi
	cd $slozka
}

inicializace() {
#echo "$1 - $2"
	parser $1
	soubor=$(echo $zdrojak | sed -r 's:\.c$::i')
	if [ "$2" = "" ]; then
		spoustak=$soubor".out"
	else
		spoustak=$(echo $2 | sed -r 's:\.out$::i')".out"
	fi
	touch $spoustak
}

pak() {
	if [ "$1" != "0" ] ; then
		echo -e "\e[1;39m\nStiskem libovolné klávesy se vrátíte do hlavního menu.\n Stiskem kláves 0-5/9 provedete patřičnou činost."
	fi
	echo -ne "\e[1;30m Stiskem Enter přejdete na "; polozka_menu $ent
	echo -ne "\e[1;30m a stiskem mezerníku na "; polozka_menu $mez
	IFS="."
	read -sn 1 vol
	if [ "$vol" = "" ]; then
		vol=$ent
	elif [ "$vol" = " " ]; then
		vol=$mez
	fi	
	unset IFS
}

nacteni() {
	clear
	while ( true ) do
		echo -e "\e[1;34mZadejte název a cestu k souboru se zdrojovým kódem\e[1;30m"
		echo " soubor má příponu .c (ale nemusí mít)"
		echo " nezáte-li nic, zvolí se výchozí (~/C/program.c)"
		read -e -i "~/" zadcesta
		if [ "$zadcesta" = "" ]; then
			zadcesta=$HOME"/C/program.c"
		fi
		parser $zadcesta
		if [ "$zdrojak" = "" ]; then 
			echo -e "\e[1;31mZadejte validní název souboru!!!"
			continue
		fi 
		if ! [ -d $slozka ] ; then 
			echo -e "\e[1;36mSložka $slozka neexistuje! Přejte si ji vytvořit? \e[1;30m"
			echo "Enter - ano, jiná klávesa - ne"
			read -sn 1 vol
			if [ "$vol" = "" ]; then
				mkdir $slozka
				echo -e "\e[1;32mSložka vytvořena"
				break
			fi
		else
			break
		fi
	done
	cd $slozka
	echo -e "\n\e[1;32mZadejte jméno spouboru výsledného programu \e[1;30m"
	echo " nebo nic pokud se má jmenovat stejně jak zdrojový (tedy $soubor.out)"
	read -e zadspoustak
	inicializace $zadcesta $zadspoustak
	vytvoreni #kdyz uz existuje stejne zkonci
	pak
}

vytvoreni() {
	mez="0"
	ent="1"
	if [ -f $zdrojak ] ; then 
		echo -e "\e[1;32mSoubor načten." 
		return
	fi
	touch $zdrojak
	echo "/*made by C write 'n' run 2.0*/" > $zdrojak
	echo -e "\e[1;32mSoubor zdrojového kódu neexistuje, bude vytvořen. Přejete si do něj vložit základní strukturu jazyka C?\e[1;38m"
	echo " Enter - ano, jiná klávesa - Ne"
	read -n 1 -s vol
	if [ "$vol" = "" ]; then 
		echo -e "#include <stdio.h>\nint main (void) {\n\tputs(\"Funguje to!\");\n\treturn 0;\n}" >> $zdrojak
		echo -e "\e[1;32mSoubor se základní strukturou vyvořen."
	else
		echo -e "\e[1;32mSoubor vytvořen."
	fi
}

editace() {
$editor $zdrojak
ent="2"
mez="1"
vol="zobraz_menu"
}

kompilace() {
echo -e "\e[1;36mKompilace zdrojového kódu ($zdrojak) do souboru programu ($spoustak): \e[1;39m "
echo "Průběh kompilace:"
if gcc -lm $zdrojak -o $spoustak ; then
	echo -e "\e[1;32m\nKompilace proběhla úspěšně (nebo s výše uvedenými varováními).\nProgram je připraven ke spuštění."
	chmod 711 $spoustak
	ent="3"
else
	echo -e "\e[1;31m\nKompilace dokončena s výše uvedenými chybami. Program nemůže být spuštěn."
	ent="1"
fi
mez="2"
pak
}

spusteni() {
echo -e "\e[0;39m"
if ./$spoustak ; then
	echo -e "\e[1;35m-------  Program ukončen bez chyby.  ----------"
else
	echo -e "\e[1;35m------------  Program ukončen.  ---------------"

fi
ent="1"
mez="3"
pak
}

napoveda() {
echo -e "\e[0;31mNápověda k programu C write n' run 2\e[0;39m"
echo "Použití: C-wnr-2 [SOUBOR_ZDROJOVÉHO_KÓDU[.c] [SOUBOR_VÝSLEDNÉHO_PROGRAMU[.out]] | [[-h] | [--help]]]"
echo "nebo: [CESTA_K_PROGRAMU]|[./]C-wnr-2.sh [SOUBOR_ZDROJOVÉHO_KÓDU[.c] [SOUBOR_VÝSLEDNÉHO_PROGRAMU[.out]] | [[-h] | [--help]]]"
echo
echo "Nezadáte-li SOUBOR_VÝSLEDNÉHO_PROGRAMU, automaticky se zvolí se stejný název jako SOUBOR_ZDROJOVÉHO_KÓDU, s patřičnou příponou (.out)."
echo "Nezádate-li žádný parametr, ihned po spuštění přejdete do interaktivního módu Otevření souboru (viz dále), kde si můžete oba tyto soubory zvolit."
echo
echo "Přepínače -h nebo --help zobrazí tuto nápovědu a zkončí."

echo -e "\e[0;34m\nOtevření souboru\e[0;39m"
echo "Otevření souboru slouží ke změně pracovního souboru. Je voláno ihned po spuštění programu pokud jej spouštíte bez parametrů, ale lze jej kdykoliv spustit v hlavním menu stiskem 0."
echo "Nejdříve si zvolíte soubor se zdrojovým kódem (jak relativně - ../prog/Program.c, Cecko/Program.c, tak absolutně /home/$(whoami)/progC/Program.c), poté soubor hotového programu (implicitně stejný jako zdrojový). Pokud soubor neexistoval bude vytvořen a budete mít možnost do zdrojového kódu vložit základní strukturu jazyka, tak, aby byl spustitelný ihned po vytvoření, bez jakýchkoliv úprav."

echo -e "\e[0;32m\nEditace souboru\e[0;39m"
echo "Pro editaci souboru je volán patřičný textový editor. Implicitně je nastaven editor ViM, zmněnit jej můžete tak, že jeho názvem přepíšete aktuální - $editor ve 3. řádku tohoto skriptu."
echo "Podrobnější informace o tomto editoru se dozvíte na manuálové stránce - man $editor."

echo -e "\e[0;36m\nKompilace\e[0;39m"
echo "Kompilace přeloží soubor zdrojového kódu do strojového kódu a uloží do souboru výsledného programu. Pokud nebyly ve zdrojovém kódu nalezeny chyby (nebo jen varování - warning), můžete program spustit. V opačném případě jste nuceni chyby v kódu odstranit. (viz Hyperinteraktivní menu)."
echo "O kompilaci se stará program gcc, pokud jej nemáte nainstalovaný, kompilace vám nebude fungovat."

echo -e "\e[0;35m\nSpuštění zkompilovaného programu\e[0;39m"
echo "Po úspěšném zkompilování můžete samotný program spustit. Pokud program zkončí s návratovou hodnootu 0 (tedy je ukončen příkazem return 0), objeví se hláška 'Program ukončen bez chyby.', pokud byl ukončen s chybou (nenulový návratový kód) nebo s žádným (svým během došel až na konec hlavního programu a nevrátil tak žádnou hodnotu) objeví se hláška 'Program ukončen.'."

echo -e "\e[0;31m\nHyperinteraktivní menu\e[0;39m"
echo "Program je vybaven tzv. hyperinteraktivním menu. To znamená, že program předvídá, co máte v plánu a tuto predikovanou akci tak můžete provádět stiskem 1 klávesy (ve skutečnosti máte na výběr ze dvou). Program tak můžete bez problémů ovládat 1 (případně 2) klávesami. Jsou to klávesy Enter a mezerník. Enter provádí vždy následují akci, zatímco mezerník vždy zopakuje tu právě provedenou."
echo "Pro zjednodušení je u každé situace, kdy je po uživateli očekáván stisk libovolné klávesy se mu zobrazí možnosti ('Stiskem Enter přejdete k ...', a tak přesně víte, která klávesa co dělá."
echo "Kromě těchto fungují i klasické číselné (0, 1, 2, 3, 4 a 9)- stejně jako v hlavním menu."

echo -e "\e[0;33m\nCopyright\e[0;39m"
echo "Tento program byl vytvořen v textovém editoru ViM, 9. - 16. října 2011. (tyto dva údaje nemají společné, to co si myslíte :-), made by m@rtlin."
echo "Licenční poznámka: Program je freeware (volně šířitelný), open-source (s otevřeným kodem (ale nedporučuji do něj nahlížet - hrozí vážné zdravotní následky)), podléhající licenci Creative Commons (můžete použít dál, ale uveďte autora)."
echo -e "\e[1;30m\nChyby hlaste na martlin[zavináč]seznam.cz\nAutor programu neručí zá žádné škody způsobené tímto programem (jako je zavaření procesoru při kompilaci)!!!\e[0;39m\n"


if [ "$1" != "--" ]; then
	pak
fi
}

polozka_menu() {
case $1 in
        "0" ) echo -e "\e[1;34motevření-načtení souboru"; return ;;
        "1" ) echo -e "\e[1;32meditaci zdrojového souboru"; return ;;
        "2" ) echo -e "\e[1;36mkompilaci"; return ;;
        "3" ) echo -e "\e[1;34mspuštění zkompilovaného programu"; return ;;
esac
}

menu() {
echo -e "\e[1;31m C write 'n' run 2.0\n\e[1;30m Vývojové prostředí pro jazyk C\e[0;39m\n made by m@rtlin 9. - 16. řijna 2011\n\e[0;31m\n\n HLAVNÍ MENU\n ===========\e[0;39m\n"

echo -e "\e[0;34m  0 - Otevření souboru"
echo -e "\e[0;32m  1 - Editace souboru"
echo -e "\e[0;36m  2 - Kompilace"
echo -e "\e[0;35m  3 - Spuštění zkompilovaného programu\n"
echo -e "\e[0;31m  5 - Nápověda"
echo -e "\e[0;38m  9 - Ukončení"
echo -e "\n\e[1;30m-------------------------------------------------\n"
echo -e "\e[0;39mAktuální adresář: \e[0;36m$slozka\e[0;39m"
echo -e " Soubor zdrojového kódu: \e[0;34m$zdrojak\e[0;39m $(wc $zdrojak | sed -r  's:([0-9]+) +([0-9]+) +([0-9]+) +.*:(Řádků\: \1, Slov\: \2, Znaků\: \3)\n:g')"
echo -e " Soubor hotového programu: \e[0;32m$spoustak\e[0;39m (Bytů: $(wc -c $spoustak | sed -r 's: .*$::'))"
echo -e "\n\e[1;30mPožadovanou akci zvolte stiskem číselné klávesy nebo Mezerníku / Enteru pro zjednodušenou volbu:"
pak "0" 
}

#HLAVNÍ PROGRAM
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then 
	napoveda "--"
	exit 0
fi
inicializace $1 $2
if [ "$soubor" = "" ]; then
	nacteni #když nebyl zvolen jako parametr
else
	vytvoreni #už ho zná, pokusí se ho vytvořit
fi
while ( true ); do
	clear
	case $vol in
		"0" ) nacteni ;;
		"1" ) editace ;;
		"2" ) kompilace ;;
		"3" ) spusteni ;;
		"4" ) nastaveni ;;
		"5" ) napoveda ;;
		"9" ) break ;;
		* ) menu ;; 
	esac
echo -ne "\e[0;39m"
done
