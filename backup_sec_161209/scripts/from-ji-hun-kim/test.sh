#!/bin/bash
# 첫번째 인자를 출력한다
# 처음에 인자를 갖는지 체크한다:
x=$(pwd)
echo $x
if [ "$#" -ne 1 ]; then
    echo "usage: $0 "
fi

echo "The argument is $1"
