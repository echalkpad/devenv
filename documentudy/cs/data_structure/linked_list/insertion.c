/*

https://practice.geeksforgeeks.org/problems/linked-list-insertion/1
http://www.geeksforgeeks.org/linked-list-set-2-inserting-a-node/

Please note that it's Function problem i.e.
you need to write your solution in the form of Function(s) only.
Driver Code to call/invoke your function would be added by GfG's Online Judge.*/

#include <stdio.h>
#include <stdlib.h>

/*
Structure of the linked list node is as
*/
struct node
{
	int data;
	struct node *next;
};


// InsertAtBegining : function inserts the data in front of the list
void push(struct node** headRef, int newData)
{
	struct node *new = NULL;

	new = (struct node *)malloc(sizeof(struct node));
	new->data = newData;
	new->next = *headRef;

	*headRef = new;	
}

// InsertAtEnd: function appends the data at the end of the list
void append(struct node** headRef, int newData)
{
	struct node *new = NULL;
	struct node *n = *headRef;

	new = (struct node *)malloc(sizeof(struct node));

	new->data = newData;
	new->next = NULL;

	if (n == NULL) { /* in case of head is NULL */
		*headRef = new;
	} else {
		while (n->next != NULL)
			n = n->next;
		n->next = new;
	}
}

/* Given a node prev_node, insert a new node after the given
   prev_node */
void insertAfter(struct node* prev_node, int new_data)
{
	struct node *new;

	new = (struct node *)malloc(sizeof(struct node));

	new->data = new_data;
	new->next = prev_node->next;
	prev_node->next = new;

}


// This function prints contents of linked list starting from head
void printList(struct node *node)
{
	while (node != NULL)
	{
		printf(" %d ", node->data);
		node = node->next;
	}
}

/* Driver program to test above functions*/
int main()
{
	/* Start with the empty list */
	struct node* head = NULL;

	// Insert 6.  So linked list becomes 6->NULL
	append(&head, 6);

	// Insert 7 at the beginning. So linked list becomes 7->6->NULL
	push(&head, 7);

	// Insert 1 at the beginning. So linked list becomes 1->7->6->NULL
	push(&head, 1);

	// Insert 4 at the end. So linked list becomes 1->7->6->4->NULL
	append(&head, 4);

	// Insert 8, after 7. So linked list becomes 1->7->8->6->4->NULL
	insertAfter(head->next, 8);

	printf("\n Created Linked list is: ");
	printList(head);

	return 0;
}
