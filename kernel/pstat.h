#ifndef _PSTAT_H_
#define _PSTAT_H_

#include "param.h"

struct pstat {
  int inuse[NPROC];    // 1 if slot is in use, 0 otherwise
  int tickets[NPROC];  // number of tickets this process has
  int pid[NPROC];      // PID of each process
  int ticks[NPROC];    // number of ticks each process has accumulated
};

#endif
