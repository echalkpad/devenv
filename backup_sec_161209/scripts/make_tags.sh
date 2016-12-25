#!/bin/bash

FILE_PATH=$(pwd)
PREFIX=$1

make_tags() {
	echo "make tags..."
	ctags -f tags -R $(pwd -P)
}

make_cscope() {
	echo "make cscope..."
	find $(pwd -P) \( -name '*.c' -o -name '*.cpp' -o -name '*.cc' -o -name '*.h' -o -name '*.s' -o -name '*.S' -o -name '*.dts' -o -name '*.dtsi' \) -print > cscope.files
	cscope -i cscope.files
}

pushd $(pwd) > /dev/null 2>&1		# [DIRECTORY0]
case $1 in
	kernel|KERNEL|k)
		while [ ! -d kernel -o ! -d arch -o ! -d drivers ]
		do
			cd ..
		done

		if [ -d kernel -a -d arch -a -d drivers ] ; then
			make_tags;
			make_cscope;
		fi
		;;
	bootloader|BOOTLOADER|b)
		pushd $(pwd -P) > /dev/null 2>&1		# [DIRECTORY0]
		while [ `basename $(pwd -P)` != "bootloader" ]
		do
			LOKE_PATH=$(pwd -P)
			cd ..
		done
		if [ `basename $(pwd -P)` == "bootloader" ] ; then
			cd ${LOKE_PATH}
			make_tags;
			make_cscope;
		fi
		;;
	-d)
		if [ -d $2 ] ; then
			cd $2
			echo $(pwd -P)
			make_tags;
			make_cscope;
		fi
		;;
esac
popd > /dev/null 2>&1
exit 0	# [DIRECTORY0]
