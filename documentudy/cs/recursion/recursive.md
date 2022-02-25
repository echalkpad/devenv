
# 재귀의 두가지 형태

- #1 리턴값 있음  

```
int func(x, y)
{
	1. 종료조건 : 경계값, visited
	2. 종료조건 : 목적지도착

	3. Visited 체크

	4. 재귀호출 : 
		ret = MIN/MAX( func(x+1,y), func(x,y+1)..)

	5. 리턴 return ret;
}
```
> 함수내에서 재귀 호출하는 func중 최소/최대값만 return하고 싶을때 사용.  
> return 위치가 맨 아래임  
> 점화식 사용 가능  
> Visited 체크 해제해줄 필요없음(?)
> 목적지부터 __거꾸로__ 돌아오면서 그 단계에서 바로 MIN/MAX값을 찾아서 리턴.
> 처음으로 돌아와서 마무리함.  


- #2 리턴값 없음  

```
void func(x, y, cnt)
{
	1. 종료조건 : 경계값, visited

	2. 목적지도착 return : 
		최소값 계산(cnt이용) 
	
	3. Visited 체크

	4. 재귀호출 :
		func(x+1,y, cnt+1); 
		func(x,y+1, cnt+1); 
		...
	
	5. Visited 복구
}
```
> 모든 경우의 수 탐색할때 사용(모든 재귀함수 호출)
> return 위치가 종료조건(base case) 바로 아래임.  
> 꼭 체크한 Visited를 복구 해줘야함.
> (cnt가 일종의 단계를 의미하기 때문에 다음단계에서 사용할 변수를 미리 저장해놓고(visited체크) 다음단계에서 돌아오면 다시 복구 해줘야함.  
> 목적지에 도달에서 마무리함.  
