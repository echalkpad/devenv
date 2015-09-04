#! /bin/bash

sed -i "s/^/![pic](\.\.\/image\/$1/" ./list
sed -i 's/$/)/' ./list
