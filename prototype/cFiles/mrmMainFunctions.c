
//to compile the code to .so file
//cc -fPIC -shared -o mrmMainFunctions.so mrmMainFunctions.c mrmFunctions.c
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

#ifndef __hostInterfaceCommon_h
#include "hostInterfaceCommon.h"
#endif
#ifndef __hostInterfaceMRM_h
#include "hostInterfaceMRM.h"
#endif

//static int haveServiceIp, connected;
static int msgIdCount;
static mrmIfType mrmIf;
int radioFd;

struct sockaddr_in radioAddr;
                

//_____________________________________________________________________________
//
// mrmSleepModeGet - retrieve sleep mode from radio
//_____________________________________________________________________________

int mrmSleepModeGet(int *mode)
{
    mrmMsg_GetSleepModeRequest request;
    mrmMsg_GetSleepModeConfirm confirm;
    int retVal = ERR, numBytes;

    // create request message
	request.msgType = htons(MRM_GET_SLEEP_MODE_REQUEST);
	request.msgId = htons(msgIdCount++);

    // make sure no pending messages
    mrmIfFlush();

    // send message to MRM
	mrmIfSendPacket(&request, sizeof(request));

    // wait for response with timeout
    numBytes = mrmIfGetPacket(&confirm, sizeof(confirm));

    // did we get a response from the MRM?
    if (numBytes == sizeof(mrmMsg_GetSleepModeConfirm))
    {
        // Handle byte ordering
        confirm.msgType = ntohs(confirm.msgType);
        confirm.msgId = ntohs(confirm.msgId);

        // is this the correct message type?
        if (confirm.msgType == MRM_GET_SLEEP_MODE_CONFIRM)
        {
            // Handle byte ordering
            *mode = ntohl(confirm.sleepMode);

            // status code
            retVal = OK;
        }
    }
    return retVal;
}


//_____________________________________________________________________________
//
// mrmSleepModeSet - change radio's sleep mode
//_____________________________________________________________________________

int mrmSleepModeSet(int mode)
{
    mrmMsg_SetSleepModeRequest request;
    mrmMsg_SetSleepModeConfirm confirm;
    int retVal = ERR, numBytes;

    // create request message
	request.msgType = htons(MRM_SET_SLEEP_MODE_REQUEST);
	request.msgId = htons(msgIdCount++);
	request.sleepMode = htonl(mode);

    // make sure no pending messages
    mrmIfFlush();

    // send message to MRM
	mrmIfSendPacket(&request, sizeof(request));

    // wait for response with timeout
    numBytes = mrmIfGetPacket(&confirm, sizeof(confirm));

    // did we get a response from the MRM?
    if (numBytes == sizeof(mrmMsg_SetSleepModeConfirm))
    {
        // Handle byte ordering
        confirm.msgType = ntohs(confirm.msgType);
        confirm.msgId = ntohs(confirm.msgId);

        // is this the correct message type?
        if (confirm.msgType == MRM_SET_SLEEP_MODE_CONFIRM)
        {
            // status code
            confirm.status = ntohl(confirm.status);
            // only return OK if status is OK
            if (confirm.status == OK)
                retVal = OK;
        }
    }
    return retVal;
}



//_____________________________________________________________________________
//
// mrmOpmodeGet - retrieve mode of operation from radio
//_____________________________________________________________________________

int mrmOpmodeGet(int *mode)
{
    mrmMsg_GetOpmodeRequest request;
    mrmMsg_GetOpmodeConfirm confirm;
    int retVal = ERR, numBytes;

    // create request message
	request.msgType = htons(MRM_GET_OPMODE_REQUEST);
	request.msgId = htons(msgIdCount++);

    // make sure no pending messages
    mrmIfFlush();

    // send message to MRM
	mrmIfSendPacket(&request, sizeof(request));

    // wait for response with timeout
    numBytes = mrmIfGetPacket(&confirm, sizeof(confirm));

    // did we get a response from the MRM?
    if (numBytes == sizeof(mrmMsg_GetOpmodeConfirm))
    {
        // Handle byte ordering
        confirm.msgType = ntohs(confirm.msgType);
        confirm.msgId = ntohs(confirm.msgId);

        // is this the correct message type?
        if (confirm.msgType == MRM_GET_OPMODE_CONFIRM)
        {
            // Handle byte ordering
            *mode = ntohl(confirm.opMode);

            // status code
            retVal = OK;
        }
    }
    return retVal;
}


//_____________________________________________________________________________
//
// mrmOpmodeSet - change mode of operation of radio
//_____________________________________________________________________________

int mrmOpmodeSet(int mode)
{
    mrmMsg_SetOpmodeRequest request;
    mrmMsg_SetOpmodeConfirm confirm;
    int retVal = ERR, numBytes;

    // create request message
	request.msgType = htons(MRM_SET_OPMODE_REQUEST);
	request.msgId = htons(msgIdCount++);
	request.opMode = htonl(mode);

    // make sure no pending messages
    mrmIfFlush();

    // send message to MRM
	mrmIfSendPacket(&request, sizeof(request));

    // wait for response with timeout
    numBytes = mrmIfGetPacket(&confirm, sizeof(confirm));

    // did we get a response from the MRM?
    if (numBytes == sizeof(mrmMsg_SetOpmodeConfirm))
    {
        // Handle byte ordering
        confirm.msgType = ntohs(confirm.msgType);
        confirm.msgId = ntohs(confirm.msgId);

        // is this the correct message type?
        if (confirm.msgType == MRM_SET_OPMODE_CONFIRM)
        {
            // status code
            confirm.status = ntohl(confirm.status);
            // only return OK if status is OK
            if (confirm.status == OK)
                retVal = OK;
        }
    }
    return retVal;
}



int mrmIfInit(char *destAddr)
{   int mode;
    unsigned radioIpAddr;
    #ifdef WIN32
        {
            // Initialize Windows sockets
            WSADATA wsad;
            memset(&wsad, 0, sizeof(wsad));
            WSAStartup(MAKEWORD(2, 2), &wsad);
        }
    #endif            
    // convert from string to binary
    radioIpAddr = inet_addr(destAddr);

    // make sure IP address is valid
    if (radioIpAddr == INADDR_NONE)
    {   
        printf("Invalid IP address.\n");
        return ERR;
    }

    // create UDP socket
    radioFd = (int)socket(AF_INET, SOCK_DGRAM, 0);
    if (radioFd == -1)
    {   
        printf("Unable to open socket");
        return ERR;
    }

    // initialize radio address structure
    memset(&radioAddr, 0, sizeof(radioAddr));
    radioAddr.sin_family = AF_INET;
    radioAddr.sin_port = htons(MRM_SOCKET_PORT_NUM);
    radioAddr.sin_addr.s_addr = radioIpAddr;
    // make sure radio is in active mode
    if (mrmSleepModeGet(&mode) != OK)
    {
        printf("Time out waiting for sleep mode.\n");
        // mrmSampleExit();
    }

	// print sleep mode
    printf("Radio sleep mode is %d.\n", mode);
    if (mode != MRM_SLEEP_MODE_ACTIVE)
    {
        printf("Changing sleep mode to Active.\n");
        mrmSleepModeSet(MRM_SLEEP_MODE_ACTIVE);
    }

    // make sure radio is in MRM mode
    if (mrmOpmodeGet(&mode) != OK)
    {
        printf("Time out waiting for mode of operation.\n");
        // mrmSampleExit();
    }

	// print radio opmode
    printf("Radio mode of operation is %d.\n", mode);
    if (mode != MRM_OPMODE_MRM)
    {
        printf("Changing radio mode to MRM.\n");
        mrmOpmodeSet(MRM_OPMODE_MRM);
    }

      

        //case mrmIfUsb:
            //return ERR;
}
int mrmConfigSet(mrmConfiguration *config)
{   
    mrmMsg_SetConfigRequest request;
    mrmMsg_SetConfigConfirm confirm;
    int retVal = ERR, numBytes, i;

    // create request message
	request.msgType = htons(MRM_SET_CONFIG_REQUEST);
	request.msgId = htons(msgIdCount++);
    memcpy(&request.config, config, sizeof(*config));

    // Handle byte ordering in config struct
    request.config.nodeId = htonl(config->nodeId);
    request.config.scanStartPs = htonl(config->scanStartPs);
    request.config.scanEndPs = htonl(config->scanEndPs);
    request.config.scanResolutionBins = htons(config->scanResolutionBins);
    request.config.baseIntegrationIndex = htons(config->baseIntegrationIndex);
    for (i = 0; i < 4; i++)
        request.config.segmentNumSamples[i] = htons(config->segmentNumSamples[i]);

    // make sure no pending messages
    mrmIfFlush();

    // send message to MRM
	mrmIfSendPacket(&request, sizeof(request));

    // wait for response
    numBytes = mrmIfGetPacket(&confirm, sizeof(confirm));

    // did we get a response from the MRM?
    if (numBytes == sizeof(confirm))
    {   
        // Handle byte ordering
        confirm.msgType = ntohs(confirm.msgType);
        confirm.status = ntohl(confirm.status);
      

        // is this the correct message type and is status good?
        if ((confirm.msgType == MRM_SET_CONFIG_CONFIRM ) &&
                (confirm.status == OK)){
                    retVal = OK;
                }    
        
    }
    return retVal;
}

int mrmConfigGet(mrmConfiguration *config)
{       
    mrmMsg_GetConfigRequest request;
    mrmMsg_GetConfigConfirm confirm;
    int retVal = ERR, numBytes, i;

    // create request message
	request.msgType = htons(MRM_GET_CONFIG_REQUEST);
	request.msgId = htons(msgIdCount++);

    // make sure no pending messages
    mrmIfFlush();

    // send message to MRM
	mrmIfSendPacket(&request, sizeof(request));

    // wait for response
    numBytes = mrmIfGetPacket(&confirm, sizeof(confirm));

    // did we get a response from the MRM?
    if (numBytes == sizeof(mrmMsg_GetConfigConfirm))
    {
        // Handle byte ordering
        confirm.msgType = ntohs(confirm.msgType);
        confirm.msgId = ntohs(confirm.msgId);

        // is this the correct message type?
        if (confirm.msgType == MRM_GET_CONFIG_CONFIRM)
        {
            // copy config from message to caller's structure
            memcpy(config, &confirm.config, sizeof(*config));
            // Handle byte ordering
            config->nodeId = ntohl(config->nodeId);
            config->scanStartPs = ntohl(config->scanStartPs);
            config->scanEndPs = ntohl(config->scanEndPs);
            config->scanResolutionBins = ntohs(config->scanResolutionBins);
            config->baseIntegrationIndex = ntohs(config->baseIntegrationIndex);
            for (i = 0; i < 4; i++)

            // milliseconds since radio boot
            confirm.timestamp = ntohl(confirm.timestamp);

            // status code
            confirm.status = ntohl(confirm.status);
            // only return OK if status is OK
            if (confirm.status == OK)
                retVal = OK;
        }
    }
      // print out configuration
    printf("\nConfiguration:\n");
    printf("\tnodeId: %d\n", (*config).nodeId);
    printf("\tscanStartPs: %d\n", (*config).scanStartPs);
    printf("\tscanEndPs: %d\n", (*config).scanEndPs);
    printf("\tscanResolutionBins: %d\n", (*config).scanResolutionBins);
    printf("\tbaseIntegrationIndex: %d\n", (*config).baseIntegrationIndex);
    for (i = 0 ; i < 4; i++)
    {
        printf("\tsegment %d segmentNumSamples: %d\n", i, (*config).segmentNumSamples[i]);
        printf("\tsegment %d segmentIntMult: %d\n", i, (*config).segmentIntMult[i]);
    }
    printf("\tantennaMode: %d\n", (*config).antennaMode);
    printf("\ttxGain: %d\n", (*config).txGain);
    printf("\tcodeChannel: %d\n", (*config).codeChannel);
    return retVal;
}

int mrmInfoGet(int timeoutMs, mrmInfo *info)
{
    int done = 0, retVal = ERR, numBytes, index, i;
    int timestamp;
    mrmIfTimeoutMsSet(timeoutMs);
    info->msg.scanInfo.msgId = 0;
    info->scan = 0;
    
    while (!done)
    {           
        // wait for packet with timeout
        numBytes = mrmIfGetPacket(&info->msg, sizeof(mrmMsg_FullScanInfo));
        
        // did we get a response from the MRM?
        if (numBytes == sizeof(mrmMsg_FullScanInfo))
        {
            // Handle byte ordering
            info->msg.scanInfo.msgType = ntohs(info->msg.scanInfo.msgType);
            info->msg.scanInfo.msgId = ntohs(info->msg.scanInfo.msgId);

            // is this the correct message type?
            if (info->msg.scanInfo.msgType == MRM_FULL_SCAN_INFO)
            {   
                // Handle byte ordering
                info->msg.scanInfo.sourceId = ntohl(info->msg.scanInfo.sourceId);
                info->msg.scanInfo.timestamp = ntohl(info->msg.scanInfo.timestamp);
                info->msg.scanInfo.channelRiseTime = ntohl(info->msg.scanInfo.channelRiseTime);
                info->msg.scanInfo.scanSNRLinear = ntohl(info->msg.scanInfo.scanSNRLinear);
                info->msg.scanInfo.ledIndex = ntohl(info->msg.scanInfo.ledIndex);
                info->msg.scanInfo.lockspotOffset = ntohl(info->msg.scanInfo.lockspotOffset);
                info->msg.scanInfo.scanStartPs = ntohl(info->msg.scanInfo.scanStartPs);
                info->msg.scanInfo.scanStopPs = ntohl(info->msg.scanInfo.scanStopPs);
                info->msg.scanInfo.scanStepBins = ntohs(info->msg.scanInfo.scanStepBins);
                info->msg.scanInfo.numSamplesInMessage = ntohs(info->msg.scanInfo.numSamplesInMessage);
                info->msg.scanInfo.numSamplesTotal = ntohl(info->msg.scanInfo.numSamplesTotal);
                info->msg.scanInfo.messageIndex = ntohs(info->msg.scanInfo.messageIndex);
                info->msg.scanInfo.numMessagesTotal = ntohs(info->msg.scanInfo.numMessagesTotal);

                // if this is the first message, allocate space for the entire waveform
                if (info->msg.scanInfo.messageIndex == 0)
                {
                    if (info->scan)
                        free(info->scan);
                    info->scan = malloc(info->msg.scanInfo.numSamplesTotal * sizeof(mrm_int32_t));
                    if (info->scan == NULL)
                    {
                        printf("Out of memory!\n");
                        return ERR;
                    }
                    index = 0;
                }
                if (info->scan)
                {
                    for (i = 0; i < info->msg.scanInfo.numSamplesInMessage; i++)
                        *(info->scan + index + i) = ntohl(info->msg.scanInfo.scan[i]);
                    index += info->msg.scanInfo.numSamplesInMessage;
                    if (info->msg.scanInfo.messageIndex == info->msg.scanInfo.numMessagesTotal-1)
                    {
                        done = 1;
                        retVal = OK;
                    }
                }

            }
        }        
        else
        {
            // timed out waiting, return error
            done = 1;
        }
    }
    return retVal;
}

int mrmControl(mrm_uint16_t msrScanCount, mrm_uint32_t msrIntervalTimeUs)
{   
    mrmMsg_ControlRequest request;
    mrmMsg_ControlConfirm confirm;
    int retVal = ERR, numBytes;

    // create request message
	request.msgType = htons(MRM_CONTROL_REQUEST);
	request.msgId = htons(msgIdCount++);

    // Handle byte ordering
    request.msrScanCount = htons(msrScanCount);
    request.msrIntervalTimeMicroseconds = htonl(msrIntervalTimeUs);

    // make sure no pending messages
    mrmIfFlush();

    // send message to MRM
	mrmIfSendPacket(&request, sizeof(request));

    // wait for response with timeout
    numBytes = mrmIfGetPacket(&confirm, sizeof(confirm));

    // did we get a response from the MRM?
    if (numBytes == sizeof(confirm))
    {
        // Handle byte ordering
        confirm.msgType = ntohs(confirm.msgType);
        confirm.status = ntohl(confirm.status);

        // is this the correct message type and is status good?
        if ((confirm.msgType == MRM_CONTROL_CONFIRM) &&
                (confirm.status == OK))
            retVal = OK;
    }
    return retVal;
}

// void mrmIfClose(void)
// {   
// #ifdef WIN32
//         // windows cleanup code
//         closesocket(radioFd);
//         WSACleanup();
// #else
//         // Linux cleanup code
//         close(radioFd);
// #endif
// }

int mrmSleepModeSetEth()
{   
    int mode = MRM_SLEEP_MODE_STANDBY_ETH;
    mrmMsg_SetSleepModeRequest request;
    mrmMsg_SetSleepModeConfirm confirm;
    int retVal = ERR, numBytes;

    // create request message
	request.msgType = htons(MRM_SET_SLEEP_MODE_REQUEST);
	request.msgId = htons(msgIdCount++);
	request.sleepMode = htonl(mode);

    // make sure no pending messages
    mrmIfFlush();

    // send message to MRM
	mrmIfSendPacket(&request, sizeof(request));

    // wait for response with timeout
    numBytes = mrmIfGetPacket(&confirm, sizeof(confirm));

    // did we get a response from the MRM?
    if (numBytes == sizeof(mrmMsg_SetSleepModeConfirm))
    {
        // Handle byte ordering
        confirm.msgType = ntohs(confirm.msgType);
        confirm.msgId = ntohs(confirm.msgId);

        // is this the correct message type?
        if (confirm.msgType == MRM_SET_SLEEP_MODE_CONFIRM)
        {
            // status code
            confirm.status = ntohl(confirm.status);
            // only return OK if status is OK
            if (confirm.status == OK)
                retVal = OK;
        }
    }
    return retVal;
}

void mrmIfClose(void)
{
    switch (mrmIf)
    {
        case mrmIfIp:
#ifdef WIN32
            // windows cleanup code
            closesocket(radioFd);
	        WSACleanup();
#else
            // Linux cleanup code
            close(radioFd);
#endif
            break;

        case mrmIfSerial:
        case mrmIfUsb:
#ifdef WIN32
            CloseHandle(hComm);
#else
            close(radioFd);
#endif
            break;

        default:
            printf("Unknown interface type.\n");
            exit(-1);
            break;
    }
}


void mrmSampleExit()
{
    mrmIfFlush();
    mrmIfClose();
    exit(0);
}

