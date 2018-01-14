## 유용한 bash shell script 코드 조각


### - 1. 현재 디렉토리 내용이 파일인지 경로인지 구분하기

```bash
#! /bin/bash

dir_search() {

	for v in $(ls $1) ; do
		if [[ -d $v ]]; then
			echo $v is directory
		elif [[ -f $v ]]; then
			echo $v is file
		fi
	done
}

dir_search $1

```

### - 2. 단순한 재귀 함수 (ls 경로탐색)


```bash
#! /bin/bash

recursion () {

	echo $v
	for v in $(ls $1)
	do
		recursion $1/$v
	done
}

recursion $1

```


### - 3. 단순한 재귀 함수 (. 에서 모든 dir 탐색)

```bash
#! /bin/bash

recursion () {

	echo $1
	for v in $(ls $1)
	do
		if [[ -d $1/$v ]]
		then
			recursion $1/$v
		fi
	done
}

recursion $(pwd)

```

### - 4. 단순한 재귀 함수 
(. 에서 모든 dir 탐색 및 파일인지 dir인지 출력)

```c
dir_search () {

	for v in $(ls $1)
	do
		if [[ -d $1/$v ]]
		then
			echo $1/$v is directory
			dir_search $1/$v
		elif [[ -f $1/$v ]]
		then
			echo $1/$v is file
		fi
	done
}

dir_search $1
```
