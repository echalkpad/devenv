TODO:
 setup.sh rm 옵션추가: 설치된 경로 삭제하고 vimrc 추가 된부분 제거
 구글번역기능: 블럭지정 후 tt하면 구글번역 엔진에서 검색해서 결과표시
 숙어검색 가능 여부 체크( "+y 로 클립보드 복사 가능여부)
     :echo has('clipboard')  또는, $vim --version  시 +clipboard 인지확인. (- 면 안됨)
     .apt-get install vim-gnome 설치.
     http://vimcasts.org/blog/2013/11/getting-vim-with-clipboard-support/
 utility/scripts/vimdic 말고, usr/local/bin/vimdic  에 설치.
     .bashrc 에 추가할 필요가 없어짐.
 locale -a 확인 시 ko_KR.utf8 / ko_KR.UTF8 대소문자 구분 없애기.
 w3m 정상 동작 확인후 설치. 설치후 정상 동작여부 확인.
프로그램 설치되어있는지 확인하는방법 찾기 (wget, w3m)
 검색햇던 단어 히스토리 관리ㅡ 단어장만들어주기 학습기능
제일많이 찾은단어 등 통계 랭킹 기능
많이찾은 단어 기반 학습
그날 검색했던 단어들 취합해서 메일로보내줌 ㅡ단어 포함되어 있던 예문포함되면 더  좋음
홈 디렉터리 . 파일로 기록 저장 및 읽기
 setup.sh  에 vimrc 에 map tt 있는지.확인후. 없으면. 추가하기.
 wget 으로 파싱하기. w3m 대신. (vimdic.sh)
 setup.sh 에서 w3m 설치 제거.
 -rm mode 에서 vimrc 파일 추가 내용도 지우기
다음줄로 끊겨있는 숙어 검색안되는 문제
발음 읽기 기능  실행되면 바로 읽어줌
발음 기호 보여주기
예문 보여주기 , 모든 번역된 예문 찾아서 보여주기
찾으려는 단어 및 숙어가 포함되고 번역이 되어있는 상태의 모든 예문 같이 출력
모든예문을 찾아 보여주는것은 해당 문장이나  표현을 다른사람이 어떻게 번역했는지 알아볼 수 있음.
로그인 기능추가하여 검색히스토리 및 통계정보 서버에 저장시킴
폰으로 보던기사 공유기능으로 PC의 vim에서 바로 열리는 기능
Http로시작하는 웹페이지주소가 인자로오면 ViM으로 페이지 텍스트 열어보기. ㅡ 가독성을 위해 해당 기능수행시 컬러스킴 변경
     기본 컬러스킴확인
:!echo $VIMRUNT I ME
Vi실행시 특정 컬러스킴으로 열기
Vim -c "colorscheme morning" 파일이름
제목 표시해주기 wget 으로 <title> </title> 사이 문자 파싱
재설치 기능 vimdic.sh 교체
웹페이지 열기 기능
-w 옵션제거하고 http일때 바로
열었을때 페이지 제목으로 커서 위치시키기
Wget으로열었을때 <title> </title>사이에있는 문장이 제목
숙어검색에서 vi 클립보드 복사 방법수정
Xmap  tt y<ESC>:!vimdic.sh<space><C-R>"<CR>   으로 수정
rm 모드에서 sed -i "/^nmap tt/d"  ~ 로변경
클립보드 설치부분 제거
Pdf read 기능 xpdf , pdftotext -nopgbrk 이용
vimdic.sh 파라미터 $@ 로 변경(여러파라미터 동시에 받기) 미리 변수에 저장해놔야함. 먼저 http 구분하는 기능 추가해야 됨
버그 : unable to get local issuer certificate: accept? (y/n)  나올때 처리 간단한방법은 y입력
터미널에서 input으로 한글 입력하면 영어뜻 출력
숙어에서 Is are was ware 를 be로 바꿔서 검색
.vimdic_history에 검색했던거 관리 기록.
