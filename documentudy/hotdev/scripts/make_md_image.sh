#! /bin/bash
# Making link of image by markdown syntax
# Using this script at the hotdev/image/.
# Usage : image $ ../scripts/make_md_image.sh 16****
# and next useful vim shortcut is "ty"

ls $1/ > $1/list
sed -i "s/^/![pic](\.\.\/image\/$1\//" ./$1/list
sed -i 's/$/)/' ./$1/list

vi -c :vs+:bn $1/list ../contents/$1.md
