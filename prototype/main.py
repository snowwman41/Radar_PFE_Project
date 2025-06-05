#gcc -fPIC -shared -o mrm.so mrmMainFunctions.c mrmFunctions.c -l ws2_32  //// windows
#cc -fPIC -shared -o mrm.so mrmMainFunctions.c mrmFunctions.c //// linux

from multiprocessing import Pipe,Process

from ctypes import *

from radar.mrmController import Mrm
from radar.doppler import *
from radar.dataScan import DataScan

from config.config import Config
from camera.camera import Camera

from plot_csv_logger.myCsv import MyCsv
from plot_csv_logger.logger import Logger
import time

def main(camSend,myCsv : MyCsv,stopSend,stopRec,radRec,config : Config):
    
    try:
        DataScan.config=config
        DataScan.camSend=camSend
        Doppler.config=config

        Mrm.initialize(config)
        time1=time.time()
       
        #wait for camera to give order to start acquisition
        DataScan.cameraStatus=radRec.recv()

        info=Mrm.mrmControl(config)                    
        while(Mrm.mrmInfoGet(info,config.timeout)): 
            dataScan = DataScan(info=info)
            #condition to stop the acquisition
            if time.time() - time1 >10:
                #signal to stop the camera process
                stopSend.send(1)
                break            
            if stopRec.poll() or stopSend.poll():
                break
     
        Logger.info("Radar stopped")
        
        if config.plotSaveRaw == DataMode.SAVE:
            myCsv.outputCsv(FileType.SCAN,DataScan.csvFullScan)

        if config.processDoppler and config.plotSaveDoppler == DataMode.SAVE:
            myCsv.outputCsv(FileType.FFT,Doppler.fftCsv)

    except Exception as e:
        print(e)
        Logger.error(e)
        
    finally:
        print("Execution Finished, radar put to sleep ETH mode")
        Logger.info("Execution Finished, radar put to sleep ETH mode")
        Mrm.mrmSleepModeSetEth()
        Mrm.mrmSampleExit()  
    
if __name__ == "__main__":

    # these were used for start/stop of the système
    startSend, startRec = Pipe(duplex=True)
    stopSend,stopRec=Pipe()
    
    config=Config(ipAdress="192.168.1.100",
                    scanInterval=1, #us
                    userBaseII=10,                 
                    userTxGain=63,
                    scanPerControl=65535, # run indefinitely                       
                    R1=1,
                    R2=20,
                    NFFT=11,
                    timeout=1000,
                    processDoppler=False,      
                    plotSaveDoppler=DataMode.SAVE,
                    plotSaveRaw=DataMode.SAVE,
                    camOn=True,
                    cameraSave=DataMode.SAVE,
                    camSaveQuality=5, # quality max 10
                    )
    
    myCsv=MyCsv(config)    
    start = True  
    while True:
        # put signal here to control start acquisitions
        if start:
            start = False

            while (stopRec.poll()):
                stopRec.recv() #reset the stop flag 

            camRec, camSend = Pipe(duplex=False) # notify cam loop to request read from cam after every scan read
            # savePathSend, savePathRec = Pipe()
            radRec, radSend = Pipe(duplex=False) # notify cam loop to request read from cam after every scan read
            
            mainProcess = Process(target=main,args=(camSend,myCsv,stopSend,stopRec,radRec,config))
            mainProcess.start()  
            Logger.info(f"main process {mainProcess.name} started",)

            camProcess = Process(target=Camera.initialize,args=(camRec,myCsv,stopRec,radSend,config)) # sync cam and radar data    
            camProcess.start()
            Logger.info(f"cam process {camProcess.name} started")
 
