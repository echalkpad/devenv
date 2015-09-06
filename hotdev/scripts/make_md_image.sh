#! /bin/bash
# Making link of image by markdown syntax

ls $1/ > $1/list
sed -i "s/^/![pic](\.\.\/image\/$1\//" ./$1/list
sed -i 's/$/)/' ./$1/list
