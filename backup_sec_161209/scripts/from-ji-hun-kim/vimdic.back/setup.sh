#!/bin/bash
SET_DIR=~/utility/scripts/vimdic
IS_FRST_SET=$(grep -c vimdic ~/.bashrc)
if [ $IS_FRST_SET == 0 ]; then
	echo "Setting vimdic.."
	sudo apt-get install w3m
	mkdir -p $SET_DIR
	cp setup.sh vimdic.sh $SET_DIR
	chmod 775 $SET_DIR/vimdic.sh
	echo "map tt :!vimdic.sh<Space><cword><CR>">> ~/.vimrc
	echo "export PATH=$PATH:$SET_DIR">> ~/.bashrc
	source ~/.bashrc
else
	echo "Vimdic already set"
fi
