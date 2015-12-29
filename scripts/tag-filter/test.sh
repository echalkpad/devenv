#! /bin/bash
# func2 구현해보기

func() {
	
	for v in 현재 디렉토리($1) ls 해보기
		if $v == 파일
			if 저장해도됨? ==> 현재 dir의 makefile과 .conifg 두파일을 열러서 확인
				저장
		if $v == dir
			if 들어가도 됨?
				func $1/$v
}

func2 () {

	for v in ./makefile에서 한줄씩 읽기
		if [[ obj-y임? || CONFIG y 임? ]] ==> .config 에서 확인
			for comp in $v의 3번째 항목부터 출력
				if file
					저장 $1/$comp
				if dir
					func2 $1/$comp

}

func2-1 () {

	for v in ./makefile에서 한줄씩 읽기
		if file
			if [[CONFIG y 임? ==> .config 에서 확인 ]]
				for f in $v의 3번째 항목부터 출력
					저장 $1/$f
		if dir
			if (CONFIG y임? || obj-y임?)
				for f in $v의 3번째 항목부터 출력
					func2 $1/$f

}


func3 () {
	for v in tags 파일 한줄씩 읽기(두번째 항목출력)
		$v가 빌드된것인지 확인	

}



dir_from_mk () {
	# $1 Makefile
	# return dir paths
	open makefile
	# .config와 비교
	#obj-y 의 3번째 항목부터 끝라인까지 echo
}

dir_search () {

	for v in $(ls $1)
	do
		if [[ $v == "Makefile" ]]
		then
			echo $1/$v is makefile
#			check_makefile $1/$v

			if [[ -d $1/$v ]]
			then
				echo $1/$v is directory
				dir_search $1/$v
			fi
		fi
	done
}

dir_search $1
