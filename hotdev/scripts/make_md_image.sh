#! /bin/bash
# Making link of image by markdown syntax
# Using this script at the hotdev/image/.

ls $1/ > $1/list
sed -i "s/^/![pic](\.\.\/image\/$1\//" ./$1/list
sed -i 's/$/)/' ./$1/list
