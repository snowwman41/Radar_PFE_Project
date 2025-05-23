from .ctypesStruct import *
from config.config import Config
from plot_csv_logger.logger import *
import math
class Mrm:
    #initialize the radar
    @classmethod
    def initialize(cls,config):
        mrmConfig=mrmConfiguration()
        mrmConfig.baseIntegrationIndex = config.userBaseII
        mrmConfig.scanStartPs = config.userScanStart
        mrmConfig.scanEndPs = config.userScanStop
        mrmConfig.txGain = config.userTxGain
        mrmConfig.scanResolutionBins = config.scanResolutionBins

        mrmIfInit(bytes(config.ipAdress,'utf-8'))
        
        connected=mrmConfigSet(byref(mrmConfig)) 
        if connected == -1:
            raise Exception("Radar not initialized")   

    #order radar to start scanning    
    @staticmethod
    def mrmControl(config):
        mrmControl(config.scanPerControl,config.scanInterval)
        info=mrmInfo()     #Structure that contains the whole data in C          
        return info         
    
    #starts reading data from UDP socket 
    @staticmethod
    def mrmInfoGet(info,timeout):      
        retValue = mrmInfoGet(1000,byref(info))==0 
        return retValue
    
    @staticmethod
    def mrmSampleExit():
        mrmSampleExit()

    @staticmethod
    def mrmSleepModeSetEth():
        mrmSleepModeSetEth()
    
   


