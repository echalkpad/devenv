#! /bin/bash
ls | grep .h | cut -d . -f 1 | while read line; do mv $line.h $line.md; done
