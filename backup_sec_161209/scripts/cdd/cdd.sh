#! /bin/bash

function cd_back() {
	DIR="./"
	OPTION=$1

	if [[ $@ -eq 0 ]]; then
		cd ../
	elif [[ "$@" == "--help" ]]; then
		echo "[cdd] : easy to go to previous directory"
		echo "Usage : cdd \"number\""
		echo "Example : cdd 3 == cd ../../../"
	else
		CNT=$OPTION
		while [ $CNT -gt 0 ]
		do
			DIR+="../"
			CNT=$(($CNT - 1))
		done
		echo go to $DIR
		cd $DIR
	fi

}
alias cdd='cd_back'
