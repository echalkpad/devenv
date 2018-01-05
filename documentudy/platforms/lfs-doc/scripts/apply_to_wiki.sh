#! /bin/bash

LFSDOC_PATH=~/project/lfs-doc
LFSWIKI_PATH=~/project/lfs-doc.wiki

#git checkout master
#git show > $LFSWIKI_PATH/from_lfs_doc.patch
#cd  $LFSWIKI_PATH
#patch -p1 < from_lfs_doc.patch
#git diff
#rm -v $LFSWIKI_PATH/from_lfs_doc.patch
#cd  $LFSWIKI_PATH
#git add --all
#git commit -m 'sync with /lfs/lfs-doc upstream/master'
#git push origin master


cp $LFSDOC_PATH/*.md $LFSWIKI_PATH/

cd  $LFSWIKI_PATH
git add --all
git commit -m 'sync with upstream/master from /lfs/lfs-doc'
git push origin master
