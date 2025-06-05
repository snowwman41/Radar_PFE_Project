from ctypes import *
import os
from numpy.ctypeslib import ndpointer

ROOT_DIR=os.path.dirname(os.path.abspath(__file__))

SO_FILE_PATH=os.path.join(ROOT_DIR,'mrm.so')
if os.name=="nt":
    import pathlib
    SO_FILE_PATH=pathlib.PureWindowsPath(SO_FILE_PATH).as_posix()

mrm_uint8_t = c_ubyte
mrm_int16_t = c_short
mrm_uint16_t = c_ushort
mrm_int32_t = c_int32
mrm_uint32_t = c_uint32
mrm_int64_t= c_int64
mrm_uint64_t= c_uint64

MRM_MAX_SCAN_SAMPLES=350
MRM_MAX_DETECTION_COUNT=350

class mrmMsg_DetectionListInfo(Structure):
    _fields_ = [
        ("msgType", mrm_uint16_t),
        ("msgId", mrm_uint16_t),
        ("numDetections", mrm_uint16_t),
        ("reserved", mrm_uint16_t),
        ("detections", mrm_uint16_t * MRM_MAX_DETECTION_COUNT)  
    ]

class mrmMsg_FullScanInfo(Structure):
    _fields_ = [
        ("msgType", mrm_uint16_t),
        ("msgId", mrm_uint16_t),
        ("sourceId", mrm_uint32_t ),
        ("timestamp", mrm_uint32_t ),
        ("channelRiseTime", mrm_uint32_t ),
        ("scanSNRLinear", mrm_uint32_t ),
        ("ledIndex", mrm_int32_t),
        ("lockspotOffset", mrm_int32_t),
        ("scanStartPs", mrm_int32_t),
        ("scanStopPs", mrm_int32_t),
        ("scanStepBins", mrm_uint16_t),
        ("scanFiltering", mrm_uint8_t),
        ("reserved", mrm_uint8_t),  
        ("antennaId", mrm_uint8_t),
        ("operationMode", mrm_uint8_t),
        ("numSamplesInMessage", mrm_uint16_t),
        ("numSamplesTotal", mrm_uint32_t ),
        ("messageIndex", mrm_uint16_t),
        ("numMessagesTotal", mrm_uint16_t),
        ("scan", mrm_int32_t * MRM_MAX_SCAN_SAMPLES)  
    ]

class msg(Union):
    _fields_ = [
        ("detectionList", mrmMsg_DetectionListInfo),
        ("scanInfo", mrmMsg_FullScanInfo)
    ]

class mrmInfo(Structure):
    # 'scan' is a pointer to the array of the full wave scan (multiple (350 or less) scans gathered from msg.scanInfo.scan  )
    # if a full wave scan has 1000 samples for example we would get 3 msg.scanInfo.scan with 350,350 and 300 
    # and they are put together in the scan ptr by the c program
    _fields_ = [
        ("msg", msg),
        ("scan", ndpointer(mrm_int32_t, flags="C_CONTIGUOUS"))
    ]

class mrmConfiguration (Structure):
    _fields_= [("nodeId",mrm_uint32_t),
	
	("scanStartPs", mrm_int32_t ),
	("scanEndPs" ,mrm_int32_t ),

	("scanResolutionBins",mrm_uint16_t ),

	("baseIntegrationIndex" ,mrm_uint16_t ),

	("segmentNumSamples" ,mrm_uint16_t*4 ),

	("segmentIntMult" ,mrm_uint8_t*4 ),
	
	# MRM_ANTENNAMODE_TXA_RXB, etc.
	("antennaMode" ,mrm_uint8_t ),

	# 0 = lowest power, 63 = highest power
	("txGain", mrm_uint8_t ),

	("codeChannel", mrm_uint8_t ),

	("persistFlag",mrm_uint8_t )]

    
myFunctions=CDLL(SO_FILE_PATH)
mrmIfInit= myFunctions.mrmIfInit

mrmIfInit.restype=c_int
mrmIfInit.argtypes=[c_char_p]

mrmControl=myFunctions.mrmControl
mrmControl.restype=c_int
mrmControl.argtypes=[c_int,c_int]


mrmConfigSet=myFunctions.mrmConfigSet
mrmConfigSet.restype=c_int
mrmConfigSet.argtypes=[POINTER(mrmConfiguration)]

mrmConfigGet=myFunctions.mrmConfigGet
mrmConfigGet.restype=c_int
mrmConfigGet.argtypes=[POINTER(mrmConfiguration)]

processInfo=myFunctions.processInfo
processInfo.restype=POINTER(c_int32)
processInfo.argtypes=[POINTER(mrmInfo)]


mrmInfoGet=myFunctions.mrmInfoGet
mrmInfoGet.restype=c_int
mrmInfoGet.argtypes=[c_int,POINTER(mrmInfo)]

mrmSleepModeSetEth=myFunctions.mrmSleepModeSetEth
mrmSampleExit=myFunctions.mrmSampleExit
