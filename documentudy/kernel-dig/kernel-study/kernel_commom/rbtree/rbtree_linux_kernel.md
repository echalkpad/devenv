  
  
# Red-Black Tree in Linux Kernel   
> 제 2 부  
(1부 "Red-Black Tree general" 먼저 읽고와야함)  

-----  
  
>                                          작성 : 김지훈 (ji_hun.kim@samsung.com)  
  
Kernel source에는 lib/rbtree_test.c 파일이 있는데  
Kernel에서 RBtree어떻게 사용하는지 친절하게 예를 들어주는 파일이다.  
이를 통해 rbtree를 어떻게 사용하는지 그리고 lib/rbtree.c 파일을 분석함으로써  
Kernel에서 rbtree의 insert / erase 동작은 어떻게 구현되었는지 분석한다.  
  
  
> 목차  
 1. 사용법 및 구조체 분석   
 2. 삽입과 삭제 연산에서 자주 사용하는 내부API 정리  
 3. 삽입 연산  
 4. 삭제 연산  
 5. References  
  
  
  
-----  
  
  
  
-----  
## 1. 사용법 및 구조체 분석   
-----  

### 1.1 개요  
Kernel의 rbtree API를 사용하려면?  
  
```txt

 1. 구조체에 struct rb_node * 멤버 추가  
 2. 전역 rb_root 구조체 변수 생성  
 3. my_insert 함수 작성  
 4. my_erase 함수 작성  

```

  























### 1.2 rb_node 구조체  
  
```c  
struct rb_node {  
	unsigned long  __rb_parent_color; /* rb parent and color */  
	struct rb_node *rb_right;  
	struct rb_node *rb_left;  
} __attribute__((aligned(sizeof(long))));  
```  
  
> 실제 rb tree규칙으로 balancing 되는 노드의 구조체.  
  
> __attribute__((aligned(sizeof(long)))); 의미는?  
구조체의 시작 주소 정렬   
구조체의 시작주소가 4또는8의 배수(long크기)가 됨.  
long형은 32bit 일때는 4byte, 64bit 일때는 8byte  
http://gcc.gnu.org/onlinedocs/gcc-4.6.1/gcc/Type-Attributes.html#Type-Attributes  

> __rb_parent_color에는 부모노드의 주소값이 long으로 형변환되어 저장된다.  
주소는 4 혹은 8의 배수로 증가하기 때문에 하위 2~3비트는 사용되지 않는다.  
rb_node에서는 이 사용하지 않는 비트를 색 지정으로 사용하여 추가 변수 필요없이 메모리 공간을 절약한다.  
그래서 rb_parent_color 멤버 변수를 통해 __부모노드 주소__와 __본인노드 색__ 두가지를 동시에 가질 수 있다.  
  
> __rb_parent_color 변수의 더 정확한 의미는 rb parent and color이다.  
  



















- linux kernel 2.4.37의 rb_node 구조체
rb_parent와 rb_color가 독립적인 변수로 존재하는것을 알 수 있다.  
메모리 공간 더 낭비됨.   

```c
typedef struct rb_node_s
{
        struct rb_node_s * rb_parent;
        int rb_color;
#define RB_RED          0
#define RB_BLACK        1
        struct rb_node_s * rb_right;
        struct rb_node_s * rb_left;
}
rb_node_t;
```
> full source http://lxr.free-electrons.com/source/include/linux/rbtree.h?v=2.4.37
  


























### 1.3 rb tree 적용된 구조체  
  
```c  
"lib/rbtree_test.c"  
struct test_node {  
	u32 key;  
	struct rb_node rb;  
	u32 val;
	u32 augmented;
}  
```  
> User가 실제 사용하는 구조체를(여기서는 struct test_node) rbtree로 구성하고 싶으면  
> 해당 구조체에 struct rb_node rb; 멤버를 추가하면 됨  
> 따라서 rbtree API에서는 rb멤버 포인터의 상위 구조체 포인터를(rb tree로 구성된 사용자 구조체가됨)  
> 얻기위해 항상 rb_entry()를 사용하는데 이게 중요(container_of랑 같음)  
  
  


















### 1.4 root 노드 생성  
아래 처럼 전역으로 rb tree의 root 초기화.  
  
```c  
"lib/rbtree_test.c"  
static struct rb_root root = RB_ROOT;  
```  

참고  
```c 
"include/linux/rbtree.h"  

#define RB_ROOT	(struct rb_root) { NULL, }

struct rb_root {
	struct rb_node *rb_node;
};

```  




  



















-----  
## 2. 삽입과 삭제 연산에서 자주 사용하는 내부API 정리  
-----  







#### - 주요 define  

```c
#define	RB_RED		0
#define	RB_BLACK	1

#define __rb_color(pc)     ((pc) & 1) 		"마지막 색지정 비트만 추출"
#define __rb_is_black(pc)  __rb_color(pc) 	"마지막 비트가 1이면 black"
#define __rb_is_red(pc)    (!__rb_color(pc)) 	"마지막 비트가 0이면 red"

#define rb_color(rb)       __rb_color((rb)->__rb_parent_color)
#define rb_is_red(rb)      __rb_is_red((rb)->__rb_parent_color)
#define rb_is_black(rb)    __rb_is_black((rb)->__rb_parent_color)

#define rb_parent(r)   ((struct rb_node *)((r)->__rb_parent_color & ~3))
#define __rb_parent(pc)    ((struct rb_node *)(pc & ~3))
"마지막 두비트를 0으로 만듦으로써 순수한 주소값으로 만듦"

```

#### - rb_entry()
container_of와 같음. 구조체 멤버 포인터를 알때 그 구조체 포인터를 얻는 매크로
rb_node 포인터를 가지고있는 my_rb_struct같은 사용자 구조체의 포인터를 얻을 수 있음.

```c
#define	rb_entry(ptr, type, member) container_of(ptr, type, member)
```














  
#### - rb_red_parent(red)
전달받은 노드의 부모노드 주소(pointer) 리턴  
__rb_parent_color 가 (struct rb_node *) 로 형변환 됨에 주의  
  
```c  
# static inline struct rb_node *rb_red_parent(struct rb_node *red)
| return (struct rb_node *)red->__rb_parent_color;
```  

#### - rb_set_parent_color(rb, p, color)  
첫번째 파라미터 rb의 부모주소변수에 p저장, 동시에 rb의 color도 지정  
두가지 일을 한번에함  
  
```c  
# static inline void rb_set_parent_color(struct rb_node *rb,  
				       struct rb_node *p, int color)  
| rb->__rb_parent_color = (unsigned long)p | color;  
```  
  
  
#### - rb_set_parent(rb, p)  
위 rb_set_parent_color 와 동일한데 따로 color지정 필요없이 색지정은 p의 색으로.  
rb의 부모주소 변수에 p 저장, 동시에 색은 p의 색으로 지정  
  
```c  
# static inline void rb_set_parent(struct rb_node *rb, struct rb_node *p)  
| rb->__rb_parent_color = rb_color(rb) | (unsigned long)p;  
```  
  



























  
  
#### - __rb_rotate_set_parents(old, new, ..., color)  
old기준으로 new를 올리는 회전연산이 일어날때 부모 변경시 사용.  
old 자리가 new로 대체 될때 사용. 부모주소 변경.  
new의 rb_parent_color에 old의 부모 주소를 저장,  
동시에 old색 color로 변경  
  
```txt  
       P               P  
      /               /  
    (O)             (N)  
    / \             / \  
   l  (N)   -->   (O)  r  
      / \         / \  
     m   r       l   m  
```  
  
```c  
# __rb_rotate_set_parents(struct rb_node *old, struct rb_node *new,  
| 		struct rb_root *root, int color)  
| struct rb_node *parent = rb_parent(old); "O의 부모노드 P 얻음"  
| new->__rb_parent_color = old->__rb_parent_color; "N의 부모로 old의 부모노드 P 지정"  
| rb_set_parent_color(old, new, color); "O의 부모로 N 지정"  
| __rb_change_child(old, new, parent, root); "P의 자식에 new연결"  
```  
  

#### - __rb_change_child(old, new, parent, ...)  
parent의 자식노드에 new연결  
(기존에 old가 parent의 어느쪽 자식이었는지에 따라서)  
  
```c  
# __rb_change_child(struct rb_node *old, struct rb_node *new,  
		  struct rb_node *parent, struct rb_root *root)  
| if (parent)  
| | if (parent->rb_left == old)  
| | | parent->rb_left = new;  
| | else  
| | | parent->rb_right = new;  
| else  
| | root->rb_node = new;  
```  
  
  














  
  
  
-----  
## 3. 삽입 연산  
-----  
  
  
```c  
"lib/rbtree_test.c"  
# static void insert(struct test_node *node, struct rb_root *root)  
| " *node : 새로 삽입할 노드, *root 현재 트리의 root 전역변수임 "  
| struct rb_node **new = &root->rb_node, *parent = NULL;  
| " **new는 처음에 root->rb_node의 포인터를 가지고 있음"  
| u32 key = node->key;  
| while ( *new)  
| | parent = *new;  
| | if (key < rb_entry(parent, struct test_node, rb)->key)  
| | " rb_entry로 얻은 현재 부모노드의 key랑 삽입노드의 key비교 "  
| | | new = &parent->rb_left;  
| | | "new는 결국 새node를 삽입할 위치를 가리키는 포인터의 포인터가 됨"  
| | else  
| | | new = &parent->rb_right;  
| rb_link_node(&node->rb, parent, new);  
| "new의 위치에 삽입할 node를 연결함"   
|---   
| "include/linux/rbtree.h"   
| # static inline void rb_link_node(struct rb_node * node, struct rb_node * parent,  
				struct rb_node ** rb_link)  
| | node->__rb_parent_color = (unsigned long)parent;  
| | "parent node의 주소를 저장함, 이 변수는 나중에 color를 지정하는 역할도 함"  
| | node->rb_left = node->rb_right = NULL;  
| | "새 node의 자식은 NULL"  
| | *rb_link = node;  
| | "삽입할 위치 rb_link에 새node 연결"  
|---   
| rb_insert_color(&node->rb, root);  
| "rb tree balancing 동작 수행"  
|---   
| # void rb_insert_color(struct rb_node *node, struct rb_root *root)  
| | __rb_insert(node, root, dummy_rotate);  
|---   
```  
> 이 insert함수는 rb tree api를 사용하여 user가 직접 구현해야하는 함수임.  
> 여기까지가 user가 구현해야할 함수  
  
  















  
- __rb_insert 분석  
  
RB tree에서 삽입하는 동작은 아래와 같이 세가지 형태 변화가 있음.  
`(소문자 : 빨간색, 대문자 검정색)`  
  
```txt  
  
Case 3 - color flips  
  
      G            g  
     / \          / \  
    p   u  -->   P   U  
   /            /  
  n            n  
  
  
Case 4 - left rotate at parent  
  
     G             G  
    / \           / \  
   p   U  -->    n   U  
    \           /  
     n         p  
  
  
Case 5 - right rotate at gparent  
  
       G           P  
      / \         / \  
     p   U  -->  n   g  
    /                 \  
   n                   U  
  
```  
> (참고) 여기서 아래 case가 1,2,3이 아닌이유는 (실제 소스코드는 1,2,3으로 되어있음)  
> rbtree_general.md 파일에서 정의한 case와 동일하게 하기위함임.  






  
```c  
# __rb_insert(struct rb_node *node, struct rb_root *root,  
| " *node : 삽입된 노드, *root 루트노드"  
| struct rb_node *parent = rb_red_parent(node), *gparent, *tmp;  
| "삽입된 노드를 이용해 루트노드 얻어옴 : parent 주소 리턴하는 함수"   
| while (true)   
| | if (!parent) "parent가 없는 root노드인경우"  
| | | rb_set_parent_color(node, NULL, RB_BLACK); "node를(root) black으로 하고 종료"  
| | | break;   
| | else if (rb_is_black(parent)) " parent가 black인 경우 문제없으므로 종료"  
| | | break;  
| | gparent = rb_red_parent(parent); " 할아버지 노드"  
| | tmp = gparent->rb_right; " 삼촌노드"  
  
| | if (parent != tmp) 	" parent == gparent->rb_left 이고"  
| | | if (tmp && rb_is_red(tmp)) "tmp는 삼촌노드가 됨, 삼촌이 빨강이면"  
| | | | " Case 3 - color flips "  
| | | |   
| | | | 	     G            g  
| | | | 	    / \          / \  
| | | | 	   p   u  -->   P   U  
| | | | 	  /            /  
| | | | 	 n            n  
| | | |   
| | | | rb_set_parent_color(tmp, gparent, RB_BLACK); "삼촌 블랙"  
| | | | rb_set_parent_color(parent, gparent, RB_BLACK); "부모 블랙으로"  
| | | | node = gparent;"현재노드 gparent로 변경"  
| | | | parent = rb_parent(node);  
| | | | rb_set_parent_color(node, parent, RB_RED); "할아버지노드 빨간색"  
| | | | continue; "현재노드는 gparent로 재귀적으로 다시 수행 while 다시반복"  
  
| | | tmp = parent->rb_right;   
| | | if (node == tmp) "현재 노드가 부모의 오른쪽 자식 이면"  
| | | | " Case 4 - left rotate at parent : left 회전 부모색 빨강"  
| | | |   
| | | | 	    G             G  
| | | | 	   / \           / \  
| | | | 	  p   U  -->    n   U  
| | | | 	   \           /  
| | | | 	    n         p  
| | | |   
| | | | parent->rb_right = tmp = node->rb_left;  
| | | | node->rb_left = parent; "parent는 현재노드의 좌측 자식으로 "  
| | | | if (tmp)  
| | | | | rb_set_parent_color(tmp, parent, RB_BLACK);  
| | | | rb_set_parent_color(parent, node, RB_RED); "parent의 부모노드주소에 node가 저장됨"  
| | | | augment_rotate(parent, node); "현재 이 함수는 dummy_rotate()이므로 무시"  
| | | | parent = node; "현재노드가 부모노드가 됨, 어차피 gparent->left는 parent였으니 이부분은 수정 필요 없음"  
| | | | "그렇다면 현재노드위치는 어디? -> 이 이후부터 p의 left(현재노드)는  
고려할 필요가 없음. 그래서 따로 현재노드를 지정해줄 필요없이 앞으로는 g와 p의 관계만만 고려하면 됨 "  
| | | | tmp = node->rb_right;  
| | | " Case 5 - right rotate at gparent "  
| | | " case 5 동작 으로 마무리"  
| | |  
| | |	      G           P  
| | |	     / \         / \  
| | |	    p   U  -->  n   g  
| | |	   /                 \  
| | |	  n                   U  
| | |  
| | | gparent->rb_left = tmp;  /* == parent->rb_right */  
| | | parent->rb_right = gparent;  
| | | if (tmp)  
| | | | rb_set_parent_color(tmp, gparent, RB_BLACK);  
| | | __rb_rotate_set_parents(gparent, parent, root, RB_RED);  
| | | "parent색을 gparent의 부모색으로 변경(==부모주소변경), gprent는 빨강으로 변경"  
| | |---   
| | | # __rb_rotate_set_parents(struct rb_node *old, struct rb_node *new,  
| | | | 		struct rb_root *root, int color)  
| | | | "old : gparent, new : parent"  
| | | | struct rb_node *parent = rb_parent(old);  
| | | | new->__rb_parent_color = old->__rb_parent_color; "parent의 부모주소 값을 gparent의 부모주소로 변경"  
| | | | rb_set_parent_color(old, new, color); "gparent의 부모주소 값을 parent 로"  
| | | | __rb_change_child(old, new, parent, root);  
| | | | " (gparent의 부모밑에 parent연결)"  
| | | |---   
| | | | "parent 자식으로 new를 연결 하는 함수"  
| | | | # __rb_change_child(struct rb_node *old, struct rb_node *new,  
| | | | | 		  struct rb_node *parent, struct rb_root *root)  
| | | | | if (parent)  
| | | | | | if (parent->rb_left == old)  
| | | | | | | parent->rb_left = new;  
| | | | | | else  
| | | | | | | parent->rb_right = new;  
| | | | | else  
| | | | | | root->rb_node = new;  
| | | |---   
| | |---   
| | | augment_rotate(gparent, parent); "dummy"
| | | break;  

| | else " 여기부터는 parent == gparent->rb_right 인 반대의 경우이고"  
| | "아래 코드는 case 3,4,5 로 위에서 분석한 내용과 방향만 반대일뿐 동일함"  
| | | tmp = gparent->rb_left;  
| | | if (tmp && rb_is_red(tmp))  
| | | | " Case 3 - color flips "  
| | | | ...  
| | | tmp = parent->rb_left;  
| | | if (node == tmp)  
| | | | " Case 4 - right rotate at parent "  
| | | | ...  
| | | " Case 5 - left rotate at gparent "  
| | | ...  
  
```  
  
  
  
















  
-----  
## 4. 삭제 연산  
-----  
  
  
```c  
"lib/rbtree_test.c"  
# static inline void erase(struct test_node *node, struct rb_root *root)  
| " *node : tree에서 삭제할 노드"  
| rb_erase(&node->rb, root);  
```  
> rb_erase만 사용하면 됨.  
> 여기까지가 user가 구현해야할 함수  
  



  
  
```c  
"lib/rbtree.c"  
void rb_erase(struct rb_node *node, struct rb_root *root)  
| struct rb_node *rebalance;  
| rebalance = __rb_erase_augmented(node, root, &dummy_callbacks);  
| "1. 노드 삭제시키고 tree가 rebalence대상이 되는지 판단"  
| if (rebalance)  
| | ____rb_erase_color(rebalance, root, dummy_rotate);  
| | "2. 삭제 연산의 rebalence 동작 수행"  
```  
  



















  
### 4.1. __rb_erase_augmented() 분석  
  
노드를 삭제하고 그자리에 successor(후계노드)를 찾아서 대체 시키는 함수  
그뒤 트리의 균형이 맞는지 rebalence가 필요한지 판단해서 리턴값으로 알려줌  
kernel에서는 leftmost successor(오른쪽 sub트리중 가장 작은 노드)를 후계노드로 선정함  
그래서 코드는 오른쪽 한방향일 경우만 고려해서 작성되어 있음

- __코드 개요__  

```c  
# __rb_erase_augmented(struct rb_node *node, struct rb_root *root,  
		     const struct rb_augment_callbacks *augment)  
| struct rb_node *child = node->rb_right, *tmp = node->rb_left;  
| struct rb_node *parent, *rebalance;
| unsigned long pc;
| "case 1"  
| if (!tmp) "오른쪽 자식만 있거나 아얘없는 경우"  
| |
| |     (n)          (s)
| |       \     ->     
| |       (s)  
| |
| | "오른쪽 자식을 대체시키고 끝"  
| | if (child) "삭제노드에 오른쪽 자식만 있는경우"  
| | | "대체된 child의 색을 삭제되는 노드색으로 (동시에 부모노드의 주소도 됨"  
| | else "삭제될 노드에 자식이 없는 경우"  
| | | "삭제될 노드 색이 black이면 5)black height규칙에 위반되기 때문에 rebalence 대상임"  
| else if (!child) "왼쪽 자식만 있는 경우"  
| | "위와 똑같이 삭제노드를 왼쪽자식으로 대체시키고 끝"  
| else "양쪽 자식이 존재하는 경우"  
| | if (!tmp) "case 2 :삭제노드의 오른자식(successor)에 왼쪽자식이 없는경우"  
| | | "이경우는 삭제노드의 오른쪽자식이 바로 후계노드가 되기 때문에 간단"  
| | |     (n)          (s)
| | |     / \          / \
| | |   (x) (s)  ->  (x) (c)
| | |         \
| | |         (c)
| | else "case 3 : 삭제노드의 오른자식에 왼쪽 sub 트리가 존재하는 경우"  
| | |
| | |    (n)          (s)
| | |    / \          / \
| | |  (x) (y)  ->  (x) (y)
| | |      /            /
| | |    (p)          (p)
| | |    /            /
| | |  (s)          (c)
| | |    \
| | |    (c)
| |   
| | "삭제노드의 왼쪽 자식은 successor의 왼쪽자식이됨"  
| | "삭제노드의 부모노드의 자식으로 successor연결"  
| | if (child2) " successor의 우측 자식(child2)이 있었다면 "
| | | "child2는 블랙으로"  
| | | "s, c둘중 적어도 하나는 무조건 블랙이었기 때문"  
| | else  
| | | "삭제 노드의 부모 노드 저장, 동시에 색은 삭제노드와 동일하게"  
| | | "successor의 기존 부모의 색이 블랙 이었다면? rebalence대상임"  
| |   
| return rebalance;  
```











  
- __코드 분석__

```c  
"include/linux/rbtree_augmented.h"  
# __rb_erase_augmented(struct rb_node *node, struct rb_root *root,  
		     const struct rb_augment_callbacks *augment)  
| struct rb_node *child = node->rb_right, *tmp = node->rb_left;  
| struct rb_node *parent, *rebalance;
| unsigned long pc;
| "case 1"  
| if (!tmp) "오른쪽 자식만 있거나 아얘없는 경우"  
| | "오른쪽 자식을 대체시키고 끝"  
| | pc = node->__rb_parent_color; "삭제할 노드의 색" 
| | parent = __rb_parent(pc); "삭제할 노드의 부모노드"  
| | __rb_change_child(node, child, parent, root); "parent의 자식에 child연결"  
| |   
| | if (child) "삭제노드에 오른쪽 자식만 있는경우"  
| | | child->__rb_parent_color = pc; "대체된 child의 색을 삭제되는 노드색으로 (동시에 부모노드의 주소도 됨"  
| | | rebalance = NULL; "rebalance필요없음"  
| | else "삭제될 노드에 자식이 없는 경우"  
| | | rebalance = __rb_is_black(pc) ? parent : NULL;  
| | | "삭제될 노드 색이 black이면 5)black height규칙에 위반되기 때문에 rebalence 대상임"  
| else if (!child) "왼쪽 자식만 있는 경우"  
| | "위와 똑같이 삭제노드를 왼쪽자식으로 대체시키고 끝"  
| else "양쪽 자식이 존재하는 경우"  
| | "kernel rbtree 에서는 leftmost successor(오른쪽 sub트리중 가장 작은 노드)를 후계노드로 대체함"  
| | struct rb_node *successor = child, *child2;  
| | tmp = child->rb_left;  
| | if (!tmp) "case 2 :삭제노드의 오른자식(successor)에 왼쪽자식이 없는경우"  
| | | "이경우는 삭제노드의 오른쪽자식이 바로 후계노드가 되기 때문에 간단"  
| | |
| | |     (n)          (s)
| | |     / \          / \
| | |   (x) (s)  ->  (x) (c)
| | |         \
| | |         (c)
| | |
| | | parent = successor; "parent는 successor를 의미"  
| | | child2 = successor->rb_right;  
| | else "case 3 : 삭제노드의 오른자식에 왼쪽 sub 트리가 존재하는 경우"  
| | |
| | |    (n)          (s)
| | |    / \          / \
| | |  (x) (y)  ->  (x) (y)
| | |      /            /
| | |    (p)          (p)
| | |    /            /
| | |  (s)          (c)
| | |    \
| | |    (c)
| | |
| | | do   
| | | | parent = successor; "y" 
| | | | successor = tmp;  
| | | | tmp = tmp->rb_left;  
| | | while (tmp); "오른자식 y 왼쪽 sub트리에서 가장 왼쪽(작은) 노드(tmp) 찾기 "  
| | | parent->rb_left = child2 = successor->rb_right;  
| | | successor->rb_right = child;  
| | | rb_set_parent(child, successor);   
| | | "삭제노드자리에 successor위치 시킴, 그에따른 자식노드 처리"  
| |   
| | "case 2,3 모두해당"  
| | successor->rb_left = tmp = node->rb_left;  
| | rb_set_parent(tmp, successor);  
| | "삭제노드의 왼쪽 자식은 successor의 왼쪽자식이됨"  
| | pc = node->__rb_parent_color;  
| | tmp = __rb_parent(pc);  
| | __rb_change_child(node, successor, tmp, root);  
| | "삭제노드의 부모노드의 자식으로 successor연결"  
| | if (child2) " successor의 우측 자식(child2)이 있었다면 "
| | | successor->__rb_parent_color = pc;  
| | | rb_set_parent_color(child2, parent, RB_BLACK);  
| | | rebalance = NULL;  
| | | "child2는 블랙으로"  
| | | " s, c둘중 적어도 하나는 무조건 블랙이었기 때문"  
| | else  
| | | unsigned long pc2 = successor->__rb_parent_color;  
| | | successor->__rb_parent_color = pc; "삭제 노드의 부모 노드 저장, 동시에 색은 삭제노드와 동일하게"  
| | | rebalance = __rb_is_black(pc2) ? parent : NULL;  
| | | "successor의 기존 부모의 색이 블랙 이었다면? rebalence대상임"  
| |   
| return rebalance;  
| "만약 rebalance가 NULL이 아니라면 return되는 rebalance는 "  
| "case 1 : n(삭제할노드)의 부모 "  
| "case 2 : successor임 (successor자체가 successor원래 부모위치로 올라가기때문)"  
| "case 3 : 대체되기 전 successor의 원래 부모 "  
|   
| "결국 삭제되는 위치(후계노드-successor이든, 실제 자식없는 삭제노드이든)의 부모노드임"  
| "successor가 없다면 (case1) -> 삭제노드의 부모노드"  
| "successor가 있다면 (case 2,3) -> 대체되기전 successor의 부모위치와 같음"  
  
```  
  














  
### 4.2. ____rb_erase_color() 분석  
  
__rb_erase_augmented() 이후   
이미 삭제할 노드는 트리에서 제거 되었고 후계자노드(successor)로 대체된 상태부터 시작됨  
매개변수로 넘어온 parent는 삭제된(대체노드) 노드의 원래 부모노드임을 주의  
  
  
- __코드 개요__  
  
```c  
# ____rb_erase_color(struct rb_node *parent, struct rb_root *root,  
	void ( *augment_rotate)(struct rb_node *old, struct rb_node *new))  
| struct rb_node *node = NULL, *sibling, *tmp1, *tmp2;  
| while (true)  
| | sibling = parent->rb_right;  
| | if (node != sibling) 	/* node == parent->rb_left */  
| | | if (rb_is_red(sibling))   
| | | | " delete_case 2 : 형제가 레드인 경우"  
| | | if (!tmp1 || rb_is_black(tmp1))   
| | | | if (!tmp2 || rb_is_black(tmp2))   
| | | | | if (rb_is_red(parent))  
| | | | | | "delete_case 4 : 형제자식 모두 블랙, 부모 레드"  
| | | | | else  
| | | | | | "delete_case 3: 형제자식 모두 블랙, 부모 블랙"  
| | | | "delete_case 5 : 무조건 형제가 검은색인경우가 됨"  
| | | | ...  
| | | "delete_case6"  
| | else	/* node == parent->rb_right */  
| | | "위와 동일한 케이스 방향만 반대"  
  
```  
> 위의 case번호는 rbtree_general.md 파일에서 규정한 번호임, 실제코드랑은 다름  
  

















  
- __코드 분석__  
  
```c  
# ____rb_erase_color(struct rb_node *parent, struct rb_root *root,  
	void ( *augment_rotate)(struct rb_node *old, struct rb_node *new))  
| struct rb_node *node = NULL, *sibling, *tmp1, *tmp2;  
| while (true)  
| | sibling = parent->rb_right;  
| | if (node != sibling) 	" node == parent->rb_left "  
| | | if (rb_is_red(sibling))   
| | | | " delete_case 2 : 형제가 레드인 경우"  
| | | | " Case 1 - Left rotate at parent"  
| | | |  
| | | | 	     P               S  
| | | | 	    / \             / \  
| | | | 	   N   s    -->    p   Sr  
| | | | 	      / \         / \  
| | | | 	     Sl  Sr      N   Sl  
| | | |  
| | | | parent->rb_right = tmp1 = sibling->rb_left;  
| | | | sibling->rb_left = parent;  
| | | | rb_set_parent_color(tmp1, parent, RB_BLACK); "형제를 블랙으로"  
| | | | __rb_rotate_set_parents(parent, sibling, root, RB_RED); "회전연산"  
| | | | sibling = tmp1; "형제를 Sl 로 변경, Sl은 무조건 블랙 이 이후 형제는 무조건 블랙"  
  
| | | tmp1 = sibling->rb_right;  
| | | if (!tmp1 || rb_is_black(tmpl1)) "형제 우측자식 블랙 이고"  
| | | | tmp2 = sibling->rb_left;  
| | | | if (!tmp2 || rb_is_black(tmp2))  "형제 좌측자식 블랙"  
| | | | | " Case 2 - Sibling color flip  
| | | | |   (p could be either color here)"  
| | | | |  
| | | | | 	     (p)           (p)  
| | | | | 	     / \           / \  
| | | | | 	    N   S    -->  N   s  
| | | | | 	       / \           / \  
| | | | | 	      Sl  Sr        Sl  Sr  
| | | | |  
| | | | | rb_set_parent_color(sibling, parent, RB_RED); "형제를 레드로"  
| | | | | if (rb_is_red(parent))  
| | | | | | "delete_case 4 : 형제자식 모두 블랙, 부모 레드 경우"  
| | | | | | rb_set_black(parent); "부모를 블랙으로"  
| | | | | else  
| | | | | | "delete_case 3: 형제자식 모두 블랙, 부모 블랙 경우"  
| | | | | | node = parent;  
| | | | | | parent = rb_parent(node);  
| | | | | | if (parent)  
| | | | | | | continue; "부모노드 기준으로 다시 처음부터"  
| | | | | break; "종료"  
  
| | | | " delete_case 5 : 무조건 형제가 검은색인경우가 됨"  
| | | | " Case 3 - Right rotate at sibling  
| | | |   (p could be either color here)"  
| | | | 	  
| | | | 	   (p)           (p)  
| | | | 	   / \           / \  
| | | | 	  N   S    -->  N   Sl  
| | | | 	     / \             \  
| | | | 	    sl  Sr            s  
| | | | 	      \              / \  
| | | | 	      tmp1        tmp1  Sr  
| | | |  
| | | | sibling->rb_left = tmp1 = tmp2->rb_right; "tmp2: sl"  
| | | | tmp2->rb_right = sibling;  
| | | | parent->rb_right = tmp2; "s 기준 right 회전연산"  
| | | | if (tmp1)  
| | | | | rb_set_parent_color(tmp1, sibling, RB_BLACK); "tmp1의 부모를 s 로"  
| | | | tmp1 = sibling;  
| | | | sibling = tmp2;  
  
| | | "delete_case6"  
| | | " Case 4 - Left rotate at parent + color flips  
| | |   (p and sl could be either color here. After rotation, p becomes black, s acquires  
| | |   p`s color, and sl keeps its color) "  
| | |   
| | | 	       (p)             (s)  
| | | 	       / \             / \  
| | | 	      N   S     -->   P   Sr  
| | | 	         / \         / \  
| | | 	       (sl) sr      N  (sl)  
| | |   
| | | parent->rb_right = tmp2 = sibling->rb_left; "tmp2: sl"  
| | | sibling->rb_left = parent;  
| | | rb_set_parent_color(tmp1, sibling, RB_BLACK); "tmp1 : sr"  
| | | "p 기준 left회전"  
| | | if (tmp2)  
| | | | rb_set_parent(tmp2, parent); "sl은 p색으로"  
| | | __rb_rotate_set_parents(parent, sibling, root, RB_BLACK); "p 기준 left회전, p색 블랙으로"  
| | | break; "종료"  
  
| | else	" node == parent->rb_right "  
| | | "여기부터는 위와 동일한 케이스 방향만 반대"  
  
```  
  
  
  
5. References  
------  
https://www.cs.usfca.edu/~galles/visualization/RedBlack.html  
http://lwn.net/Articles/184495/  
https://kldp.org/node/117200  
http://gcc.gnu.org/onlinedocs/gcc-4.6.1/gcc/Type-Attributes.html#Type-Attributes  
  
  
< Source Code >  
[lib/rbtree.c](https://github.com/torvalds/linux/blob/v4.6/lib/rbtree.c)  
[lib/rbtree_test.c](https://github.com/torvalds/linux/blob/v4.6/lib/rbtree_test.c)  
[include/linux/rbtree.h](https://github.com/torvalds/linux/blob/v4.6/include/linux/rbtree.h)  
[include/linux/rbtree_augmented.h](https://github.com/torvalds/linux/blob/v4.6/include/linux/rbtree_augmented.h)   
