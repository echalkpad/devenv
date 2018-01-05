/* 
 * member가 type의 포인터 멤버일때 container_of를 어떻게 사용하는가????
 **/

## 1
#include <stdio.h>

#define offsetof(type, member) ((size_t) &((type *)0)->member)

#define container_of(ptr, type, member) ({      \
		const typeof( ((type *)0)->member ) *__mptr = (ptr);    \
		(type *)( (char *)__mptr - offsetof(type,member) );})

struct te {
	int t;
} data;

struct type
{
	char ttt;
	int *member;
	struct te *d;
} con;

int main()
{
	con.d = &data;
	printf("%p\n", &con);
	printf("%p\n", container_of(&(con.member), struct type, member));

	printf("%p\n", &con);
	printf("%p\n", container_of(&(con.d), struct type, d));

	return 0;
}

#if 1


## 2

/**이렇게 할때 안됨다고함.**/
// http://stackoverflow.com/questions/26661643/container-of-macro-when-we-have-a-pointer-inside-a-struct

struct my_container {
    int x;
    struct some_struct *ss;
}

struct my_container *my_c;
my_c = container_of(&ss, struct my_container, ss)


/** 이렇게 하라고함 some_struct_ptr는 알고있는 포인터 **/

struct some_struct **my_struct_ptr = &some_struct_ptr;
my_c = container_of(my_struct_ptr, struct my_container, ss);

#endif


## 3 patch 파일 확인

## 4. 참고 링크
http://stackoverflow.com/questions/15832301/understanding-container-of-macro-in-linux-kernel
http://stackoverflow.com/questions/28848137/how-to-obtain-container-struct-of-a-pointer-element-using-macro-container-of


