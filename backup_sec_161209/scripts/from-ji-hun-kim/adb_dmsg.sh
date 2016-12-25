#! /bin/bash

rm ~/.dump_dmesg.h
adb shell dmesg > ~/.dump_dmesg.h
vi ~/.dump_dmesg.h
