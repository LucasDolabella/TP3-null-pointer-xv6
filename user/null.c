#include "kernel/types.h"
#include "user/user.h"

int
main(void)
{
  printf("null: dereferencing null pointer...\n");
  int *p = 0;
  printf("value at null: %d\n", *p);
  printf("null: should not reach here\n");
  exit(0);
}