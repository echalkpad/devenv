
### 1. 문제   

Perforce 에서 해당 디렉토리에 수정된 파일을 한번에 확인하는 기능인   
"Reconcile Offlie Works.." 기능은 매우 유용합니다.  
(원하는 source derectory 에서 우클릭 -> Reconcile Offlie Works..선택)  

하지만 원하지 않는 파일도 같이 검색되서 원하는 파일을 찾기 번거럽고, 탐색속도도 느리다는 단점이 있습니다.  
그래서 그 해결책을 공유드립니다.

### 2. 해결 : p4ignore 사용하기  
p4ignore 를 사용하면 간단하게 불필요한 검색대상을 무시할 수 있습니다.  
(.gitignore 와 유사한 기능)  

### 3. 방법  

- __(1). ".p4ignore" 파일 생성 및 작성.__  

```sh
 $ cd ~
 $ touch .p4ignore
```
> 파일 생성  

```sh
# directories 
.git
 
# files 
*.git 
.gitignore
tags
cscope.*
*.patch
*~
*.o
.*
```
> 파일 내용.    
> 탐색하고 싶지 않은 디렉토리나 파일을 추가로 기술 할 수 있습니다.  
> 혹은 첨부한 파일을 홈디렉토리에 위치 시키기  


- __(2). .bashrc 파일에 환경변수 추가 등록하기.__   

```sh
export P4IGNORE=$HOME/.p4ignore

```
> .bashrc 파일 하단에 추가.   


```sh
 $ source ~/.bashrc
```
> .bashrc 새로 적용   

- __(3). perforce 에서 확인!__  
