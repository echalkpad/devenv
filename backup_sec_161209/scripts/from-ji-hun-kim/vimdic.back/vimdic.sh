#!/bin/bash
SET_DIR=~/utility/scripts/vimdic
clear
w3m -dump "http://small.dic.daum.net/search.do?q=$1" > $SET_DIR/dump_dic 2>&1
grep -A1 "듣기반복듣기" $SET_DIR/dump_dic > $SET_DIR/result_dic
echo $1
sed -n "2p" $SET_DIR/result_dic
