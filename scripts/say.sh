# For mac ox x
#! /bin/bash
TTS=say
VOICE=samantha
SPEED=160
INPUT_FILE=$2
EXTFROM=aiff
EXTTO=mp3
if [[ "$1" == "-f" ]]; then
	$TTS -v $VOICE -r $SPEED -o ./$INPUT_FILE.$EXTFROM "$(cat $INPUT_FILE)"
	lame ./$INPUT_FILE.$EXTFROM ./$INPUT_FILE.$EXTTO
	rm ./$INPUT_FILE.$EXTFROM
else
	$TTS -v $VOICE -r $SPEED "$1"
fi
