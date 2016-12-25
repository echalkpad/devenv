#!/bin/bash
SETUP_PATH=~/utility/scripts/jidic
IS_FRST_SET=$(grep -c jidic ~/.bashrc)
echo "Default shortcut of vim is tt"
if [ $IS_FRST_SET == 0 ]; then
	echo "First setup of jidic"
	apt-get install w3m
	mkdir -p $SETUP_PATH
	cp setup.sh jidic.sh $SETUP_PATH
	chmod 775 $SETUP_PATH/jidic.sh
	echo "map tt :!jidic.sh<Space><cword><CR>">> ~/.vimrc
	echo "export PATH=$PATH:$SETUP_PATH">> ~/.bashrc
else
	echo "jidic already set"
fi
