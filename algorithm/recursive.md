
# 재귀의 두가지 형태

- #1 리턴값 있음  

```
int func(x,y)
{
	1. 종료조건 : 경계값, visited
	2. 종료조건 : 목적지도착

	3. Visited 체크

	4. 재귀호출 : 
		ret = MIN/MAX( func(x+1,y), func(x,y+1)..)
	5. 리턴 return ret;
}
```

- #2 리턴값 없음  

```
void func(x,y,cnt)
{
	1. 종료조건 : 경계값, visited
	2. Visited 체크

	3. 목적지도착 리턴 : 
		최소값 계산(cnt이용) 
	
	4. 재귀호출 :
		func(x+1,y, cnt+1); 
		func(x,y+1, cnt+1); 
		...
}
```


