#!/bin/bash
#vyplivne notficakni bublinu a aktualni prehravanou skladbou v mocp

notify-send --app-name=mocp --icon=/usr/share/pixmaps/mc.xpm 'Právě hraje' "$(moc-info.sh | sed 's/&/AND/g' )"

