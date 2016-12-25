#!/bin/bash
TTS=pico2wave
PLAYWAVE=aplay
WAVEFILE=~/.readtext.wav

if [ "$1" == "-f" ]; then
	$TTS -w=$WAVEFILE "$(cat $2)"
	$PLAYWAVE $WAVEFILE
	rm $WAVEFILE
else
	$TTS -w=$WAVEFILE "$1"
	$PLAYWAVE $WAVEFILE
	rm $WAVEFILE
fi
