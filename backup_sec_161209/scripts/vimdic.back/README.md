vimdic
======

Dictionary for vim linux user	
Using shortcut 'tt' which means 'translate that' to translate the word on the cursor or phrase of visual block.



####HISTORY
- 151029	
	Bug fix of #24
- 150725	
	Changing command name to vimdic from vimdic.sh		
- 150702	
	Coloring the target from example sentence	
- 150619	
	Just using argument which begins with "www" or "http" to open web page with vim.	
- 150610	
	Added feature of saving searched history	
- 150511	
	Fully working on the Mac OS X	
- 150428	
	Available installing on the Mac OS X with setup.sh	
- 150408	
	Display examples of target word and expression	
	User can select if the example will be displayed or not	
- 150326	
	It is possible to input more parameter	
	Change method of input parameter of vimdic.sh from $1,$2,$3 to $@		
- 150319	
	Improve the way copy text to copy phase to clipboard by shorcut 'tt' (<C-R>")	
	So, It does not needs to install vim-gnome	
- 150311	
	'-w [웹페이지주소]' 옵션 추가		
	Opening the web page with vim. And just using shortcut 'tt' to read long text like article more easily.	
- 150218	
	Using wget instead of w3m which set by defalut for parsing text of meaning from dictionary.	
	In -rm mode, Removing tt keymap from vimrc file	
- 150216	
	'-rm' 옵션추가. 설치 삭제 기능. (setup.sh)	
- 150214	
	코드정리. 줄바꿈.	
- 150213	
	일부 숙어검색 안되는 문제수정: 숙어검색 가능 여부 체크( "+y 로 클립보드 복사 가능여부)	
	설치경로 변경 : utility/scripts/vimdic 이 아닌 usr/local/bin/vimdic 에 설치.	
- 150129	
	Vim 에서 블럭 지정후 tt 하면 숙어 검색됨 (여러단어 검색 기능) 기존 커서 위치간어 검색도 유지	
	W3m 문자열 파싱 부분 수정. 숙어 파싱 호환, 한 단어 검색 에서 기본 숙어 출력.	
	Setup.sh 에서 한글 locale 설정 부분 보완 ko_KR.UTF-8	
	locale 설정관련이슈수정: locale -a 에서 ko_KR.utf8 이 아얘 없는경우 해결.	
- 150128	
	숙어검색 지원: vim에서 tt단축키 블럭지정 모드인지 노멀모드인지 구분해서 수행.	
- 150118	
	코드정리: SET_DIR 제거. vimdic.sh	
- 150116	
	일부 한글깨짐 이슈 수정: vimdic.sh에서. w3m실행전에. export lang 	
- 150115	
	setup.sh : 설치가 이미 되어있는지 체크 후 설치. (bashrc에서 검색)	
- 150114	
	setup.sh 설치스크립트 추가. (w3m설치, vimrc 에 추가)	
- 150106	
	vimdic.sh 생성. 기본 영어단어 뜻 출력. vimrc 수동 추가.	
