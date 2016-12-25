#!/bin/bash

Markdown.pl --html4tags $1 > $1.html
google-chrome $1.html
rm $1.html
