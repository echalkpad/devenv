#!/bin/bash

SET_DIR=/usr/local/bin
IS_LOCALE_SET=$(locale -a | grep -c ko_KR.utf8)
VD=vimdic.sh
VIMDIC=vimdic
DUMP_DIR=~/.dump_vimdic
MAC=Darwin
LINUX=Linux
WHICH_SYSTEM=$(uname -s)
PWD=$(pwd)

chmod 775 $VD
if [ "$1" == "-rm" ]; then
	if [ -f $SET_DIR/$VIMDIC ]; then
		sudo rm $SET_DIR/$VIMDIC
		sed -i "/For vimdic/d" ~/.vimrc
		sed -i "/^nmap tt/d" ~/.vimrc
		sed -i "/^xmap tt/d" ~/.vimrc
		rm $DUMP_DIR
		echo "Removing vimdic is done.."
	else
		echo "Removing vimdic is already done.."
	fi
else
	if [ -f $SET_DIR/$VIMDIC ]; then
		echo "Vimdic already set"
	else
		echo "Setting vimdic.."

		if [[ $WHICH_SYSTEM == $MAC ]]; then
			echo "On the Mac OS X"
			if which brew >/dev/null; then
				echo "Homebrew is already set."
			else
				echo "Installing Homebrew which is packages manager for OSX like 'apt-get' for debian linux"
				ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
			fi
			echo "Installing GNU utility : gnu-sed"
			brew install gnu-sed --with-default-names
		elif [[ $WHICH_SYSTEM == $LINUX ]]; then

			# Set locale to ko_KR.UTF-8
			if [ $IS_LOCALE_SET == 0 ]; then
				echo "Starting locale setting"
				sudo locale-gen ko_KR.UTF-8
				sudo dpkg-reconfigure locales
				if [ $(locale -a | grep -c ko_KR.utf8) == 0 ]; then
					echo "Fail to setup locale"
				else
					echo "Success to setup locale"
				fi
			else
				echo "Already set locale"
			fi

			echo "Installing w3m to open web page"
			sudo apt-get install w3m
		fi

		sudo ln -sv $PWD/$VD $SET_DIR/$VIMDIC
		echo "Added mapping key 'tt' into ~/.vimrc"
		echo "\" For vimdic">> ~/.vimrc
		echo "nmap tt :!vimdic<Space><cword><CR>">> ~/.vimrc
		echo "xmap tt y<ESC>:!vimdic<Space><C-R>\"<CR>">> ~/.vimrc
		source ~/.bashrc
		echo "Vimdic setup is done."
	fi
fi
