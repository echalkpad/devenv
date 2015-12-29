
## 0. 개발환경 구축  
Host : Macbook Air  
Target : Pebble Time Round  


### 0.1 SDK 다운로드 및 설치  
https://developer.getpebble.com/sdk/download/?sdk=3.8.2  

```{r, engine='bash', count_lines}
 # "If you previously used Homebrew to install the Pebble SDK, run:"
 $ brew update && brew upgrade pebble-sdk

 # "If you've never used Homebrew to install the Pebble SDK, run:"
 $ brew update && brew install pebble/pebble-sdk/pebble-sdk
```

- 참고 SDK manual 설치   
https://developer.getpebble.com/sdk/install/mac/  



### 0.2 프로젝트 생성하기.  
test-project 라는 이름으로 생성  

```{r, engine='bash', count_lines}
 $ pebble new-project test-project
 $ ls test-project/
 appinfo.json	resources	src		wscript
```
>
appinfo.json : app configure 파일  
src : 소스코드  
단순한 구조의 소스코드가 자동으로 구현되어있음.  


```{r, engine='bash', count_lines}
 $ pebble new-project test-project --simple
```
> --simple 옵션은 제일 기본구조만 만들어줌.   


### 0.3 프로젝트 빌드.  
https://developer.getpebble.com/tutorials/watchface-tutorial/part1/  

--simple 옵션 없이 생성한 프로젝트로 테스트  
프로젝트의 루트 경로에서 아래명령  

```{r, engine='bash', count_lines}
 $ pebble build
 .....
 'build' finished successfully (1.203s)

 $ ls
 appinfo.json	resources	wscript		build		src
```
> build/ 새로 생성됨  



