#!/bin/bash
x=$(grep -c vimdic ~/.bashrc)
echo $x
if [ $x == 0 ]; then
	echo "first setup"
else
	echo "jidic already setup"
fi
