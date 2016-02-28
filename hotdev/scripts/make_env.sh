#! /bin/bash
WHICH_SYSTEM=$(uname -s)
MAC=Darwin 
LINUX=Linux 
DIR="../contents"
IMG="../image"

cp $DIR/ref.md $DIR/$1.md
mkdir $IMG/$1
cp $IMG/backgound_img_maker_keynote.key $IMG/$1/

if [[ $WHICH_SYSTEM == $MAC ]]; then
	sed -i "s/150/$1/g" $DIR/$1.md
elif [[ $WHICH_SYSTEM == $LINUX ]]; then
	sed -i "s/150/$1/g" $DIR/$1.md
fi
