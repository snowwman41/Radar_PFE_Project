from gui.mainWindow import *
from gui.mainWindowController import *

from multiprocessing import Pipe,Process,Queue
from concurrent.futures import ThreadPoolExecutor

from ctypes import *

from radar.mrmController import Mrm
from radar.doppler import *
from radar.dataScan import DataScan

from config.config import Config
from camera.camera import Camera

from plot_csv_logger.plot import Plot
from plot_csv_logger.myCsv import MyCsv
from plot_csv_logger.logger import Logger
from radar.detection import *

def main(queue : Queue,camSend,myCsv : MyCsv,stopSend,stopRec,radRec,config : Config):
    
    try:
        DataScan.config=config
        DataScan.queue=queue
        DataScan.camSend=camSend 
        Doppler.config=config    
        Doppler.queue=queue

        #real time acquisition
        if config.postProcessing == -1:    
            Mrm.initialize(config)
            with ThreadPoolExecutor() as executor:
                DataScan.executor=executor 
                while True:   
                    #wait for camera to give order to start acquisition
                    radRec.recv()

                    info=Mrm.mrmControl(config)                    
                    while(Mrm.mrmInfoGet(info,config.timeout)):  
                        dataScan = DataScan(info=info)
                        
                        if stopRec.poll() or stopSend.poll():                           
                            break
                    if stopRec.poll() or stopSend.poll() :                              
                        break
                    Logger.info("Radar stopped")
            
            if config.plotSaveRaw == DataMode.SAVE:
                myCsv.outputCsv(FileType.SCAN,DataScan.csvFullScan)

            if config.plotSaveDoppler == DataMode.SAVE:
                myCsv.outputCsv(FileType.FFT,Doppler.fftCsv)


        #post processing
        else:
                 
            with ThreadPoolExecutor() as executor:
                DataScan.executor=executor 
                while not stopRec.poll() or stopSend.poll():
                    #camera controls radar when plotting
                    if radRec.poll():
                        radRec.recv()
                        break
                    # do radar processing only without plotting/ visualising
                    elif config.processSaveDetection:   
                        break
         
                for scanInfo in myCsv.multiScanInfo:
                    if stopRec.poll() or stopSend.poll() :  
                        break
                    dataScan=DataScan(info=None,scanInfo=scanInfo)              
                    if not config.processSaveDetection:
                        # give time for plot to refresh 
                        time.sleep(0.3)
                if config.processSaveDetection:
                    myCsv.outputCsv(FileType.DETECTION,Detection.csvDetectionSamples)
                    myCsv.outputCsv(FileType.NODETECTION,Detection.csvNoDetectionSamples)

                stopSend.send(1)
            return
   
    except Exception as e:
        print(e)
        Logger.error(e)
        
    finally:
        print("Execution Finished, radar put to sleep ETH mode")
        Mrm.mrmSleepModeSetEth()
        Mrm.mrmSampleExit()  

def initdatascan(info,config,prevScan ):
    return DataScan(info=info,config=config,prevScan=prevScan) 
    
def run_gui(configSend,stopSend):
    app = QApplication([])
    window = MainWindow()
    controller = MainWindowController(window,configSend,stopSend)
    window.show()
    app.exec_()
    
if __name__ == "__main__":

    configSend, configRec = Pipe(duplex=True)
    stopSend,stopRec=Pipe()
    pro=Process(target=run_gui,args=(configSend,stopSend))
    pro.start()
    
    while True:
        
        config=configRec.recv()  
        myCsv=MyCsv(config) 
        
        if config.postProcessing !=-1 :
            config=myCsv.getConfig()
        while (stopRec.poll()):
            stopRec.recv() #reset the stop flag 

        camRec, camSend = Pipe(duplex=False) # notify cam loop to request read from cam after every scan read
        radRec, radSend = Pipe(duplex=False) # notify cam loop to request read from cam after every scan read
        radarQueue = Queue()      
        
        mainProcess = Process(target=main,args=(radarQueue,camSend,myCsv,stopSend,stopRec,radRec,config))
        mainProcess.start()  
        print("main process",mainProcess.name)
        
        if not config.processSaveDetection:
            if config.plot:
                plotProcess = Process(target=Plot.initialize,args=(radarQueue,stopRec,config))    
                plotProcess.start()
                print("plot process",plotProcess.name)

        
            camProcess = Process(target=Camera.initialize,args=(camRec,myCsv,stopRec,radSend,config)) # sync cam and radar data    
            camProcess.start()
            print("cam process",camProcess.name)
 
