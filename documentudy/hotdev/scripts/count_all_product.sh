#! /bin/bash

DIR=./*

tail -n 7 $DIR | grep "[0-9]\." 

# in vim, sum of all line
# :%!awk '{print; total+=$2}END{print total}'
