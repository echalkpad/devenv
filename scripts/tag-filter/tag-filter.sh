#! /bin/bash
DEFCFG_FILE=".config"
MAKEFILE="Makefile"
OUTFILE=""

read_from_mk () {

	# input : Makefile from current path
	# output : return all of lines which includes "obj-" from input file

	local FILE=$1 	# $1 is Makefile from current path
	grep -nr obj- ./$FILE
}

get_after_obj () {
	# input : one line from Makefile
	# output : extract first component by AWK and get string after "obj-"

}

strip_parentheses () {

	# output : striped string which surrounded between "$(" and ")"
}

get_cfg_name () {

	# input : one line from Makefile
	# output : Extract precisely CONFIG_ name 
	
	local NAME=$(get_after_obj $1)
	if [[ $NAME == "y" ]]
	then 
		echo "y"
	else
		echo $(strip_parentheses $NAME)
	fi
}

check_from_defcfg () {
	# input : string "CONFIG_"
	# output : "y" or "n"
	
	# searching from $DEFCFG_FILE whether $1 is "y" or not
}

is_available () {

	# input : config name is could be "y" or "CONFIG_*"
	# output : true or false

	if [[ $1 == "y" ]]
	then
		echo true 	# TODO : true/false
	else 
		if [[ $(check_from_defcfg $1) == "y" ]]
		then
			echo true	
		else 
			echo false
		fi

	fi
}

get_file_dir_name () {
	# input : one line from Makefile 
	# output : return all of component after 3rd componemt using AWK
}

is_file () {
	# input : string
	# output : if input is "file" then return true, if not return false
}

is_dir () {
	# input : string
	# output : if input is "dir" then return true, if not return false
}

save_this_file () {
	# save $1 to $OUTFILE
}


check_makefile () {
	# input : $1 is current path

	# for line in ./makefile에서 한줄씩 읽기
	# TODO: Make문법을 확인해서 빌드가 되는 파일명이 있는 라인만 출력해야함.
	# "\"로 구분된 여러줄 처리: 한줄로 만들어서?
	# 일단은 +=, := 가 있는라인 출력
	for line in $(read_from_mk $1)
	do
		# makefile 한 줄에서 config이름 추출하기
		local CFG=$(get_cfg_name $line)

		# if [[ obj-y임? || CONFIG y 임? ]] ==> .config 에서 확인
		if [[ -참 $(is_available $CFG) ]] # TODO : 참 옵션확인
		then
			# for f in $line 의 3번째 항목부터 출력
			for comp in $(get_file_dir_name $line)
			do
				if [[ -참 $(is_file $comp) ]]
				then
					# 저장 $1/$f
					save_this_file $1/$comp
				elif [[ -참 $(is_dir $comp) ]]
				then
					# recursion $1/$f
					check_makefile $1/$comp
				fi
			done
		fi

	done
}

check_makefile $1

