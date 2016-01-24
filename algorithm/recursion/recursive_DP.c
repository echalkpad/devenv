#include <stdio.h>
#define INF 99999

int H,W,SX,SY,EX,EY;
int data[101][101];
int mem[101][101];

int min(int a, int b, int c, int d)
{
	int com1 = (a < b ? a : b);
	int com2 = (c < d ? c : d);
	return (com1 < com2 ? com1 : com2);
}

/* 
 * If The sum value around dest is over than 1, 
 * Final result has to be added "2" 
 */
int check_around(int x, int y)
{
	int sum = 0;
	if(x+1 <= H)
		sum += data[x+1][y];
	if(y+1 <= W)
		sum += data[x][y+1]; 
	if(x-1 >= 1)
		sum += data[x-1][y]; 
	if(y-1 >= 1)
		sum += data[x][y-1];
	if(sum >= 2)
		return 2;
	else 
		return -1;
}

int recur(int x, int y)
{
	int ret = 1; /* for counting visit */

	if (!data[x][y] || x > H || y > W || x < 1 || y < 1)
		return INF;

	/* Memoization */
	if (mem[x][y])
		return mem[x][y];

	if (x == EX && y == EY)
		return 1;

	data[x][y] = 0; /* Visited */

	ret += min(recur(x + 1, y), recur(x, y + 1), recur(x - 1, y), recur(x, y - 1));
	mem[x][y] = ret;

	return ret;
}

int main (void)
{
	int T, test_case;
	int i,j;
	int fin;
	freopen("sample_input.txt","r",stdin);

	scanf("%d",&T);
	for (test_case = 0; test_case < T; test_case++) {
		fin = 0;
		scanf("%d %d",&H, &W);
		scanf("%d %d",&SX, &SY);
		scanf("%d %d",&EX, &EY);
		for (i = 1; i <= H; i++) {
			for (j = 1; j <= W; j++) {
				scanf("%d", &data[i][j]);
				mem[i][j] = 0;
			}
		}

		/* Pre-calculation about When destination value is "2" */
		if (data[EX][EY] == 2)
			fin = check_around(EX,EY);
		if (fin == -1) {
			printf("#%d: %d\n", test_case, fin);
			continue;
		}

		printf("#%d: %d\n", test_case, recur(SX,SY) + fin);
	}
	
	return 0;
}
