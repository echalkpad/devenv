#!/bin/sh
if [ "$1" = "-w" ]; then
	w3m -dump "http://en.wikipedia.org/wiki/$2" > ~/utility/scripts/wiki/dump_wiki 2>&1 
else
	w3m -dump "$1" > ~/utility/scripts/wiki/dump_wiki 2>&1 
fi
vim -c "colorscheme morning" ~/utility/scripts/wiki/dump_wiki
