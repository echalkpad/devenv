#!/bin/bash
SOURCE_ROOT_DIR=$(pwd)
KERNEL_DIR="${SOURCE_ROOT_DIR}/android/kernel"
BOOTLOADER_PARENT_DIR="${SOURCE_ROOT_DIR}/android/bootable/bootloader"

if [ ! -d ${KERNEL_DIR} ] ; then
	echo -e "no such kernel directory(DIR : ${KERNEL_DIR})"
	KERNEL_DIR=""
fi

if [ ! -d ${BOOTLOADER_PARENT_DIR} ] ; then
	echo -e "no such bootloader directory(DIR : ${BOOTLOADER_PARENT_DIR}"
else
	BOOTLOADER_DIR=`zenity --file-selection --directory --filename=${BOOTLOADER_PARENT_DIR}/* --title="Choose Bootloader"`
	if [ -z "${BOOTLOADER_DIR}" ] ; then
		echo -e "no such bootloader directory(DIR : ${BOOTLOADER_PARENT_DIR})"
	fi
fi

if [ -z ${KERNEL_DIR} ] && [ -z ${BOOTLOADER_DIR} ] ; then
	echo -e "no target directory for tag and cscope"
	exit 0	# [DIRECTORY0]
fi

if [ -f "tags" ] ; then
	rm tags
fi

echo "make ctags..."
ctags -f tags -R $KERNEL_DIR $BOOTLOADER_DIR
if [ -f "tags" ] ; then
	echo "tags has been created successfully."
else
	echo -e "fail : tags not created"
fi

if [ -f "cscope.files" ] ; then
	rm cscope.files
fi

if [ -f "cscope.out" ] ; then
	rm cscope.out
fi

echo "make cscope..."
find $KERNEL_DIR \( -name '*.c' -o -name '*.cpp' -o -name '*.cc' -o -name '*.h' -o -name '*.s' -o -name '*.S' \) -print > cscope.files
find $BOOTLOADER_DIR \( -name '*.c' -o -name '*.cpp' -o -name '*.cc' -o -name '*.h' -o -name '*.s' -o -name '*.S' \) -print >> cscope.files
cscope -i cscope.files
if [ -f "cscope.out" ] ; then
	echo "cscope.out has been created successfully."
else
	echo -e "fail: cscope.out not created"
fi
