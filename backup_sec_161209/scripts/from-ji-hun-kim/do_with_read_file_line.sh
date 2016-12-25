#!/bin/bash

while read line
do
	#TODO something
	echo $line
	touch $line.mkd
#	./prob_mk.sh $line
done < $1
