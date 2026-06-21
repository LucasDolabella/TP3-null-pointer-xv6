#include "kernel/types.h"
#include "kernel/pstat.h"
#include "user/user.h"

int
main(void)
{
  // Give this process 2 tickets, child gets 1 (inherited default).
  settickets(2);

  int pid = fork();
  if(pid < 0){
    fprintf(2, "fork failed\n");
    exit(1);
  }

  if(pid == 0){
    settickets(1);  // child gets 1 ticket, parent keeps 2
    volatile int x = 0;
    for(;;) x++;
  }

  // Parent: spin for a while, then check ticks
  volatile int x = 0;
  for(int i = 0; i < 500000000; i++) x++;

  struct pstat ps;
  if(getpinfo(&ps) < 0){
    fprintf(2, "getpinfo failed\n");
    kill(pid);
    exit(1);
  }

  int my_ticks = 0, child_ticks = 0;
  int my_pid = getpid();

  for(int i = 0; i < NPROC; i++){
    if(!ps.inuse[i]) continue;
    if(ps.pid[i] == my_pid)    my_ticks    = ps.ticks[i];
    if(ps.pid[i] == pid)       child_ticks = ps.ticks[i];
  }

  printf("parent (2 tickets): %d ticks\n", my_ticks);
  printf("child  (1 ticket):  %d ticks\n", child_ticks);
  printf("ratio: %d:%d (expected ~2:1)\n", my_ticks, child_ticks);

  kill(pid);
  wait(0);
  exit(0);
}
