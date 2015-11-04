

``git remote -v`` 했을때  
github.com/vimdic/vimdic이 origin으로 등록 되어있어서 upstream으로 이름 변경해야함.  

```sh
 $ git remote -v
origin	https://github.com/vimdic/vimdic (fetch)
origin	https://github.com/vimdic/vimdic (push)
```

```sh
 $ git remote rename upstream origin
```

그리고 다시 내가 포크한 원격저장소 github.com/jihuun/vimdic 를 origin에 등록함.  
앞으로 소스수정은 origin에 하고 origin에서 upstream으로 Pull Request날릴 것임.  


정상 동작의 모습  
```sh
 $ git remote -v
origin	https://github.com/jihuun/vimdic (fetch)
origin	https://github.com/jihuun/vimdic (push)
upstream	https://github.com/vimdic/vimdic (fetch)
upstream	https://github.com/vimdic/vimdic (push)
```


근데 아직 local의 master가 upstream/master를 tracking하고 있음.  
이럴때 git pull하면 upstream에서 fetch-merge하게 됨.  
```sh
 $ git branch -vv
  * master             7e98c5b [upstream/master] Fix bugs from changing command name
```
> 추적 브랜치 확인 ``git branch -vv``  

브랜치 추적 변경  
```sh
 $ git branch -u origin/master 
Branch master set up to track remote branch master from origin.
```

정상  
```sh
 $ git branch -vv
  * master             7e98c5b [origin/master] Fix bugs from changing command name
```




Reference  
https://git-scm.com/book/ko/v2/Git-%EB%B8%8C%EB%9E%9C%EC%B9%98-%EB%A6%AC%EB%AA%A8%ED%8A%B8-%EB%B8%8C%EB%9E%9C%EC%B9%98
