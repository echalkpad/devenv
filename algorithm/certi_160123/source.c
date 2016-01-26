#include <stdio.h>
#define NOTFND	-2
#define NOBALL	-1

int data[10];
int max;
int N;
enum { LEFT = 0, RIGHT, };

int find_b(int in, int dir)
{
	int ret = NOTFND;
	int i = 0;
	if (dir == RIGHT) {
		for (i = in + 1; i < N; i++) {
			if (data[i] != NOBALL) {
				ret = i;
				break;
			}
		}
	} else {
		for (i = in - 1; i >= 0; i--)
			if (data[i] != NOBALL) {
				ret = i;
				break;
			}
	}
	return ret;
}

/*
1. 양쪽둘다 있는경우 둘다 곱함
2. 한쪽만 있는 경우 그값 그대로
3. 혼자만있는 경우 자신의값
*/
int calc(int in)
{
	int ret = 0;
	int left_in = find_b(in, LEFT); //index of left ballun
	int right_in = find_b(in, RIGHT);

	if ((left_in != NOTFND) && (right_in != NOTFND))
		ret = data[left_in] * data[right_in];
	
	if ((left_in != NOTFND) && (right_in == NOTFND))
		ret = data[left_in];

	if ((left_in == NOTFND) && (right_in != NOTFND))
		ret = data[right_in];

	if ((left_in == NOTFND) && (right_in == NOTFND))
		ret = data[in];
	
	return ret;
}

void recur(int index, int cnt, int result)
{
	int tmp;
	int i;
	int st = 0;
	int st_index = 0;

	/* Calculation */
	result += calc(index);

	/* Base case */
	if (cnt == N) {
		if (result > max)
			max = result;
		return;
	}

	/* Visited */
	tmp = data[index];
	data[index] = NOBALL;
	cnt++;

	/* Sort of Pruning */
	st_index = find_b(0, RIGHT);
	if (st_index == NOTFND)
		st = 0;
	else
		st = st_index;

	/* Recursion */
	for(i = st; i < N; i++)
		if (data[i] != NOBALL)
			recur(i, cnt, result);

	data[index] = tmp;
}

int main (void)
{
	int T, test_case;
	int i,j;

	freopen("sample_input.txt","r",stdin);

	scanf("%d",&T);
	for (test_case = 1; test_case <= T; test_case++) {
		max = 0;
		scanf("%d",&N);
		for (i = 0; i < N; i++)
			scanf("%d", &data[i]);
		
		for (i = 0; i < N; i++)
			recur(i, 1, 0);

		printf("#%d: %d\n", test_case, max);
	}
	
	return 0;
}
