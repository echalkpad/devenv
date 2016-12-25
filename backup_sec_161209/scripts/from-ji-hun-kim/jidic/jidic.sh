#!/bin/sh
SETUP_PATH=~/utility/scripts/jidic
clear
w3m -dump "http://small.dic.daum.net/search.do?q=$1" > $SETUP_PATH/dump_dic 2>&1 
grep -A1 "듣기반복듣기" $SETUP_PATH/dump_dic > $SETUP_PATH/result_dic
echo $1
sed -n "2p" $SETUP_PATH/result_dic
