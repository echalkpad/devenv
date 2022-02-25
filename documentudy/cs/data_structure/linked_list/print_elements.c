/*
   https://practice.geeksforgeeks.org/problems/print-linked-list-elements/1

   Please note that it's Function problem i.e.
   you need to write your solution in the form of Function(s) only.
   Driver Code to call/invoke your function would be added by GfG's Online Judge. */

/*
   Print elements of a linked list on console 
   head pointer input could be NULL as well for empty list
   Node is defined as 

   struct Node
   {
	   int data;
	   Node *next;
   }
*/

#include <stdio.h>

void display(struct Node *head)
{
	//your code goes here
	struct Node *n = head;

	while (n != NULL) {
		printf("%d ", n->data);
		n = n->next;
	}
}
