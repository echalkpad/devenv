
__attribute__ 란?

http://blog.daum.net/english_100/5

```c
struct rb_node
{
	unsigned long  rb_parent_color;
	struct rb_node *rb_right;
	struct rb_node *rb_left;
}__attribute__((aligned(sizeof(long))));
```
의미는?

http://gcc.gnu.org/onlinedocs/gcc-4.6.1/gcc/Type-Attributes.html#Type-Attributes

long 이 32bit에서는 4byte 64bit에서는 8byte인데,
원래 구조체가 메모리에 할당될때는 (Int와 char가 멤버로 있는경우) char는 1만
할당되는것이 아니라 int와 같은 메모리로 할당되어서 구조체는 총 8 byte가
할당됨(3byte낭비됨) 하지만 이게 메모리 접근에 더빠르고 용이함.


}__attribute__((aligned(sizeof(long))));
이 의미는 long 크기만큼 각 멤버를 할당하라는것
그래서 rb_parent_color 멤버는 부모노드주소와 본인노드 색을 동시에 가질 수 있다.

