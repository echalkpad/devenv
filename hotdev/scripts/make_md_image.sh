#! /bin/bash

sed -i "s/^/![pic](\.\.\/image\/$1\//" ./$1/list
sed -i 's/$/)/' ./$1/list
