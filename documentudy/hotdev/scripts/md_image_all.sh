#! /bin/bash
ls | cut -d . -f 1 | while read line;
do
	pwd
	../scripts/make_md_image.sh $line
done
