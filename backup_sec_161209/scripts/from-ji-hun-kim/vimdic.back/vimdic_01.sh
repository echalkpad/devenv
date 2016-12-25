#!/bin/bash
clear
echo $1
w3m -dump -no-cookie "http://small.dic.daum.net/search.do?q=$1" | grep -A1 "듣기반복듣기" | sed -n "2p"
