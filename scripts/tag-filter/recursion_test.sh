#! /bin/bash
# 모든 dir의 파일 ls해보기

dir_search () {

	for v in $(ls $1)
	do
#		echo $v "*"
		if [[ -d $1/$v ]]
		then
			echo $v is directory
			dir_search $1/$v
			#ls $v
		elif [[ -f $1/$v ]]
		then
			echo $v is file
		fi
	done
}

recursion () {

	local PATH

	echo $1
	for v in $(ls $1)
	do
		PATH=$1/$v

		if [[ -d PATH ]]
		then
			recursion PATH
		fi
	done
}

recursion $1
#dir_search $1
