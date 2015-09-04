#! /bin/bash
ls | cut -d . -f 1 | while read line;
do
	cd $line/
	make_md_image.sh $line
done
