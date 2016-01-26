#! /bin/bash

read_from_mk () {

	# input : Makefile from current path
	# output : return all of lines which includes "obj-" from input file

	local FILE=$1 	# $1 is Makefile from current path
	grep -nr obj- $FILE
}

read_from_mk $1
