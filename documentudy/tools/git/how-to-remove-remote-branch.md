
원격저장소에 등록되어있는 지저분한 브랜치들 삭제하기.  

``$ git remote show origin`` origin의 브랜치 정보 확인  
``$ git push origin --delete 브랜치명`` remote branch 삭제  

```sh
 $ git remote show origin

* remote origin
  Fetch URL: https://github.com/jihuun/Linux-Documentation-KOR-Translation
  Push  URL: https://github.com/jihuun/Linux-Documentation-KOR-Translation
  HEAD branch: master
  Remote branches:
    Fix-linux/README           tracked
    development-process/Intro  tracked
    dp/intro                   tracked
    dp/intro-branch            tracked
    dp/process                 tracked
    dp/process-2               tracked
    dp/process_2               tracked
    linux/README--translating  tracked
    master                     tracked
    minimizing-target-document tracked
    update-firstpage           tracked
  Local branch configured for 'git pull':
    master merges with remote master
  Local ref configured for 'git push':
    master pushes to master (up to date)
```



너무 많아서 스크립트로  
```sh
#! bin/bash

git push origin --delete Fix-linux/README           
git push origin --delete development-process/Intro  
git push origin --delete dp/intro                   
git push origin --delete dp/intro-branch            
git push origin --delete dp/process                 
git push origin --delete dp/process-2               
git push origin --delete dp/process_2               
git push origin --delete linux/README--translating  
git push origin --delete minimizing-target-document 
git push origin --delete update-firstpage           

```

이제 ``$ git remote show origin`` 해보면 master만 남아있음.  



Reference  
https://git-scm.com/book/ko/v2/Git-%EB%B8%8C%EB%9E%9C%EC%B9%98-%EB%A6%AC%EB%AA%A8%ED%8A%B8-%EB%B8%8C%EB%9E%9C%EC%B9%98
