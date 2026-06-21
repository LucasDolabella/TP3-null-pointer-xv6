#include "kernel/types.h"
#include "kernel/stat.h"
#include "user/user.h"

int main(int argc, char *argv[])
{
  int syscall_num;

  syscall_num = atoi(argv[1]);
  int count = getcnt(syscall_num);

  printf("syscall %d has been called %d times\n", syscall_num, count);
  exit(0);
}
