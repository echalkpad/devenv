#!/bin/bash
export LANG=ko_KR.UTF-8
clear
w3m -dump -no-cookie "http://small.dic.daum.net/search.do?q=$1 $2 $3" | sed -n -e "/영어 사전/,/영어 사전 더보기/p" | sed -e "/^영어 사전/d" | sed -e "/^\[/d"
