/* https://practice.geeksforgeeks.org/problems/delete-a-node-in-single-linked-list/1 */

/*
   Please note that it's Function problem i.e.
   you need to write your solution in the form of Function(s) only.
   Driver Code to call/invoke your function would be added by GfG's Online Judge. */

// A complete working C program to demonstrate deletion in singly
// linked list
#include <stdio.h>
#include <stdlib.h>

// A linked list node
struct Node
{
	int data;
	struct Node *next;
};


void deleteNode(struct Node **head, int x)
{
	struct Node *n = *head;

	/* #1 in case of object is head */
	if (n->data == x) {
		*head = n->next;
		free(*head);
		return;
	}

	/* finding prev node; n is prev node */
	while (n->next != NULL && n->next->data != x) {//n->next is the object to delete
		n = n->next;
	}

	/* #2 in case of no object */
	if (n->next == NULL) {
		printf("no object %d", x);
		return;
	}

	n->next = n->next->next;
	free(n->next);
}

/* Given a reference (pointer to pointer) to the head of a list
   and a position, deletes the node at the given position */
void deleteNode_position(struct Node **head_ref, int position)
{
	struct Node *prev, *n = *head_ref;
	int i;

	/* deletion head */
	if (position == 0) {
		*head_ref = n->next;
		free(*head_ref);
		return;
	}

	/* finding prev node of deletion node */
	for (i = 0; i < position && n->next != NULL; i++) {
		prev = n;
		n = n->next;
	}

	/* no position */
	if (i <= position - 1) {
		printf("no position\n");
		return;
	}

	/* deletion n */
	prev->next = n->next;
	free(n);
	
}

/* Given a reference (pointer to pointer) to the head of a list
   and an int, inserts a new node on the front of the list. */
void push(struct Node** head_ref, int new_data)
{
	struct Node* new_node = (struct Node*) malloc(sizeof(struct Node));
	new_node->data  = new_data;
	new_node->next = (*head_ref);
	(*head_ref)    = new_node;
}

// This function prints contents of linked list starting from 
// the given node
void printList(struct Node *node)
{
	while (node != NULL)
	{
		printf(" %d ", node->data);
		node = node->next;
	}
}

/* Drier program to test above functions*/
int main()
{
	/* Start with the empty list */
	struct Node* head = NULL;
	int x;

	push(&head, 7);
	push(&head, 1);
	push(&head, 3);
	push(&head, 2);
	push(&head, 8);
	push(&head, 4);
	push(&head, 5);

	puts("Created Linked List: ");
	printList(head);
	printf("\nchoose position or node ");
	scanf("%d", &x);
	//deleteNode(&head, x);
	deleteNode_position(&head, x);
	puts("\nLinked List after Deletion ");
	printList(head);
	puts("");
	return 0;
}
