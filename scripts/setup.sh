#!/bin/bash

SCRIPT_NAME=cdd
SET_DIR=/usr/local/bin
CUR_PATH=$(pwd -P)

echo "Symbolic link $SCRIPT_NAME.sh to "$SET_DIR"/$SCRIPT_NAME"
sudo ln -s $CUR_PATH/cdd.sh $SET_DIR/cdd

echo " ">> ~/.bashrc
echo "# for script cdd">> ~/.bashrc
echo "source /usr/local/bin/cdd">> ~/.bashrc
source /usr/local/bin/cdd
source ~/.bashrc
