

어떤 구조체 내의 내부 포인터를 알고 있을때   
해당 구조를 포함하는 상위 구조체의 정보를 참조할때 유용한 방법이다.    

```c  

#define container_of(ptr, type, member) ({          \
const typeof( ((type *)0)->member ) *__mptr = (ptr);    \
(type *)( (char *)__mptr - offsetof(type,member) );}) 
```
 
>  
3개의 파라메터를 입력으로  
ptr : 현재 알고있는 구조체내의 멤버 포인터  
type : ptr을 포함하고 있는 구조체의 원형 (알고싶은 구조체)  
member : type구조체에서 ptr의 멤버명 (알고싶은 구조체에서 ptr멤버명)  
  
#define container_of(멤버포인터, 구조체 원형, 구조체 멤버 종류)
  
http://guruseed.org/205525748  
  
