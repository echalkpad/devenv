#! /bin/bash
WHICH_SYSTEM=$(uname -s)
DIR="../contents"
IMG="../image"

cp $DIR/ref.h $DIR/$1.h
mkdir $IMG/$1

if [[ $WHICH_SYSTEM == $MAC ]]; then
	sed -i '' "s/150/$1/g" $DIR/$1.h
elif [[ $WHICH_SYSTEM == $LINUX ]]; then
	sed -i "s/150/$1/g" $DIR/$1.h
fi
