#! /bin/bash

# Using awk
# http://www.hiscience.com/tech/archives/286
# awk '조건 {액션}' 참조파일
# 참조명령 | awk '조건 {액션}'

# PS=$(ps -A | grep synergy  | awk '$4=="synergy" {print $1}')
PS=$(ps -A | awk '$4 ~/^synergy/ {print $1}')

kill $PS
