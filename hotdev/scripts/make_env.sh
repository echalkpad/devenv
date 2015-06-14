#! /bin/bash
WHICH_SYSTEM=$(uname -s)
DIR="../contents"

cp $DIR/ref.h $DIR/$1.h
mkdir $DIR/image/$1

if [[ $WHICH_SYSTEM == $MAC ]]; then
	sed -i '' "s/150/$1/g" $DIR/$1.h
elif [[ $WHICH_SYSTEM == $LINUX ]]; then
	sed -i "s/150/$1/g" $DIR/$1.h
fi
