
#ifndef __hostInterfaceCommon_h
#include "hostInterfaceCommon.h"
#endif
#ifndef __hostInterfaceMRM_h
#include "hostInterfaceMRM.h"
#endif


int getSamlesTotal(mrmInfo *info);
int processInfos(mrmInfo *info,int *i);


void mrmIfTimeoutMsSet(int tmoMs);
int mrmIfGetPacketIp(void *pkt, unsigned maxSize);
int mrmIfGetPacket(void *pkt, unsigned maxSize);
int mrmIfSendPacketIp(void *pkt, unsigned size);
int mrmIfSendPacket(void *pkt, unsigned size);
void mrmIfFlush(void);
