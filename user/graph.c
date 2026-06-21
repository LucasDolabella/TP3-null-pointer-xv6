#include "kernel/types.h"
#include "kernel/pstat.h"
#include "user/user.h"

#define SAMPLES   10
#define INTERVAL  50   // uptime ticks between samples

int
main(void)
{
  int pids[3];
  int tickets[3] = {30, 20, 10};

  // Fork 3 children; each gets a different ticket count
  for(int i = 0; i < 3; i++){
    settickets(tickets[i]);
    pids[i] = fork();
    if(pids[i] < 0){
      fprintf(2, "fork failed\n");
      exit(1);
    }
    if(pids[i] == 0){
      // Child: spin forever
      volatile int x = 0;
      for(;;) x++;
    }
  }

  // Parent: restore default tickets so it barely interferes
  settickets(1);

  printf("sample\tA(30)\tB(20)\tC(10)\n");

  struct pstat ps;
  int prev[3] = {0, 0, 0};

  for(int s = 0; s < SAMPLES; s++){
    // Wait INTERVAL ticks
    uint t0 = uptime();
    while(uptime() - t0 < INTERVAL)
      ;

    if(getpinfo(&ps) < 0){
      fprintf(2, "getpinfo failed\n");
      break;
    }

    int cur[3] = {0, 0, 0};
    for(int i = 0; i < NPROC; i++){
      if(!ps.inuse[i]) continue;
      for(int j = 0; j < 3; j++){
        if(ps.pid[i] == pids[j])
          cur[j] = ps.ticks[i];
      }
    }

    // Print ticks gained since last sample
    printf("%d\t%d\t%d\t%d\n",
      s + 1,
      cur[0] - prev[0],
      cur[1] - prev[1],
      cur[2] - prev[2]);

    for(int j = 0; j < 3; j++) prev[j] = cur[j];
  }

  // Print totals
  printf("total\t%d\t%d\t%d\n", prev[0], prev[1], prev[2]);

  // Kill children
  for(int i = 0; i < 3; i++){
    kill(pids[i]);
    wait(0);
  }

  exit(0);
}