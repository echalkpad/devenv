
Android Kerenl Hacks 책 참고.


주요파일 
drivers/clk/*
drivers/clk/samsung/*


주요 구조체

```c

struct clk_foo {
	struct clk_hw hw;
	... /* hw specific data */
}

struct clk_hw {
	struct clk *clk;
	...
}

struct clk {
	struct clk_ops ops;
	...
}

struct clk_ops {
	/* 각 soc에서 정의한 clk관련 ops 함수 callback등록 필요 */
}

```
> 
.prepare
.enable
.round_rate
.set_rate
.recalc_rate
등등이 있음.

실제 clk_enable(hw); 를 호출하면 결국 각 soc파일에서 정의한 ops 콜백이 호출됨.  
