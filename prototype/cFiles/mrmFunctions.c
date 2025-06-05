#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifdef WIN32
#include "winsock2.h"
#else // linux
#include <arpa/inet.h>
#include <sys/select.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <unistd.h>
#endif

#ifndef __mrmFunctions_h
#include "mrmFunctions.h"
#endif

static int timeoutMs = DEFAULT_TIMEOUT_MS;

static int msgIdCount;

extern int radioFd;
extern struct sockaddr_in radioAddr;



int *processInfo(mrmInfo *info){    
    return info->scan;
}

void mrmIfTimeoutMsSet(int tmoMs)
{
    timeoutMs = tmoMs;
}

int mrmIfGetPacketIp(void *pkt, unsigned maxSize)
{
	fd_set fds;
    struct timeval tv;

    tv.tv_sec = timeoutMs / 1000;
    tv.tv_usec = (timeoutMs * 1000) % 1000000;

    // basic select call setup
	FD_ZERO(&fds);
	FD_SET(radioFd, &fds);

	// Set up timeout


	if (select(radioFd + 1, &fds, NULL, NULL, &tv) > 0)
	{
		// copy packet into buffer
		return recvfrom(radioFd, (char *)pkt, maxSize, 0, NULL, NULL);
	}
	// Timeout
	return ERR;
}

int mrmIfGetPacket(void *pkt, unsigned maxSize)
{
    //if (mrmIf == mrmIfIp)
    return mrmIfGetPacketIp(pkt, maxSize);
    //else
        //return mrmIfGetPacketSerial(pkt, maxSize);
}
int mrmIfSendPacketIp(void *pkt, unsigned size)
{
	return sendto(radioFd, (const char *)pkt, size, 0,
            (struct sockaddr *)&radioAddr, sizeof(radioAddr));
}
int mrmIfSendPacket(void *pkt, unsigned size)
{
    //if (mrmIf == mrmIfIp)
    return mrmIfSendPacketIp(pkt, size);
    /*else
        return mrmIfSendPacketSerial(pkt, size);*/
}
void mrmIfFlush(void)
{
    int tmp, i = timeoutMs;

    timeoutMs = 0;
    while (mrmIfGetPacket(&tmp, sizeof(tmp)) > 0)
        ;
    timeoutMs = i;
}
