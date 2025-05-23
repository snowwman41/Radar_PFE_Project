import time
from statistics import mode
from ctypes import *
from concurrent.futures import ThreadPoolExecutor

import radar.ctypesStruct as MRM
from .doppler import *

from plot_csv_logger.myCsv import *
from common.enums import DataMode

from .dataProcessing import *
from .detection import Detection

class DataScan:
         
    """ 
    doppler/detection processing affect the acquisition performances of l'orin even when processing is on threads, 
    and since the acquisition protocole is in UDP/Ip,  data is lost, a malloc error ( kept on purpose) is raised. 
    this error appears especially when chunks of data are big ( long distances of radar detections ) and the scan 
    interval for scans is low, which wont leave sufficient time between the acquisitions of scans.

    """

    executor : ThreadPoolExecutor
     
    #doppler
    dopplerIterator=0
    
    #csv
    saveDetection=True
    csvFullScan= []

    def __init__(self,*,info,scanInfo=None):

        if Detection.iteratorDataScan>= Detection.windowSize -1 and not Detection.isDetectionBoxFull:
            Detection.isDetectionBoxFull=True

        # dont sync with camera if generating detection data 
        if not DataScan.config.processSaveDetection:
            DataScan.camSend.send(1) 
        
        self.systemTimestamp=time.perf_counter_ns() if scanInfo is None else scanInfo[0]
        self.numSamplesTotal=info.msg.scanInfo.numSamplesTotal if scanInfo is None else len(scanInfo[2:]  )
        self.dataScan=np.ctypeslib.as_array(MRM.processInfo(info) ,shape=(self.numSamplesTotal,)) if scanInfo is None else np.array(scanInfo[2:])  
        self.timestamp=info.msg.scanInfo.timestamp if scanInfo is None else None
        self.detectionArray=np.empty(self.numSamplesTotal,dtype=np.int8)

        if DataScan.config.plotSaveRaw == DataMode.SAVE:
            DataScan.csvFullScan.append([self.systemTimestamp,self.timestamp,*self.dataScan])
        
        # detection processing
        if DataScan.config.processDetection:
            Detection.filterData(self)
            Detection.appendEnvelopeToDataBox(self)
            if Detection.isDetectionBoxFull:                
                Detection.calculateDetection(self)                          
            Detection.iteratorDataScan +=1

        # doppler processing
        if DataScan.config.processDoppler: 
            Doppler.multiIQScan.append(Doppler.IQTransform(self))        
            DataScan.dopplerIterator+=1
            if DataScan.dopplerIterator == DataScan.config.NFFT:               
                Doppler.processFFT(self)

        # populate Queue for plotting
        if DataScan.config.processDetection:
            if Detection.isDetectionBoxFull:
                if DataScan.config.processDoppler and (DataScan.dopplerIterator == DataScan.config.NFFT ) and DataScan.config.plot:     
                    DataScan.queue.put({"dataScan": self.dataScan,"detectionIndices": self.indices,"detectionArray":self.detectionFinal[self.condition],"doppler": self.FFTSCN})
                    DataScan.dopplerIterator=0
                elif DataScan.config.plot: 

                    DataScan.queue.put({"dataScan": self.dataScan,"detectionIndices": self.indices,"detectionArray":self.detectionFinal[self.condition]})
            else:
                if DataScan.config.processDoppler and (DataScan.dopplerIterator == DataScan.config.NFFT ) and DataScan.config.plot:     
                    DataScan.queue.put({"dataScan": self.dataScan,"doppler": self.FFTSCN})
                    DataScan.dopplerIterator=0

        elif DataScan.config.processDoppler and DataScan.dopplerIterator == DataScan.config.NFFT and DataScan.config.plot:
            DataScan.queue.put({"dataScan": self.dataScan, "doppler": self.FFTSCN})  
            DataScan.dopplerIterator=0

        elif DataScan.config.plot:
            DataScan.queue.put({"dataScan":self.dataScan})
            




    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    @staticmethod
    def hilbert_from_scratch(u):
        pass
        # N : fft length
        # M : number of elements to zero out
        # U : DFT of u
        # v : IDFT of H(U)
        
        # N = len(u)
        # # take forward Fourier transform
        # U = fft(u)
        # M = N - N//2 - 1
        # # zero out negative frequency components
        # U[N//2+1:] = [0] * M
        # # double fft energy except @ DC0
        # U[1:N//2] = 2 * U[1:N//2]
        # # take inverse Fourier transform
        # v = ifft(U)
        # return v      

        # if config.processVelocity==0:
        #     return
        #cls.multiDataScan.append(dataScanObj.dataScan)
        #IQ=hilbert(np.array(dataScanObj.dataScan))  scipy hilbert version gives only the imaginary part/ can be modified in the scipy library 
                                                    #hilbert_from_scratch is an equivalent version that gives both real + imaginary with same performance     
        # DataScan.multiDataScan.append(self.dataScan)
        
        # if DataScan.fftIterator ==32: 
                      
        #     scanEnv=enveloppe(( np.subtract(self.dataScan,self.prevDataScan)))  
        #     # scanEnv=enveloppe(( np.subtract(np.mean(DataScan.multiDataScan[28:30],axis=0),np.mean(DataScan.multiDataScan[30:32],axis=0)))) 
          
        #     DataScan.scanEnvProcessed.append(np.minimum((np.around((63*(scanEnv))/(10e3)))+ 1 , 64)) # appended just for the print
        #     Idet= [value>=10 for value in DataScan.scanEnvProcessed[DataScan.rangeIterator-1]] # need to be changed to self.scanEnv in the future ( no need to append data)
        #     DataScan.rangeIterator=DataScan.rangeIterator+1
        #     # print(scanEnv)
        #     multiIQScan=np.transpose(np.array(DataScan.multiIQScan))    
        #     FFT=fft(multiIQScan,n=32,axis=1) #NFFT=32       
        #     ABSFFT=np.absolute(FFT)   
        #     ABSFFT[:,0]=0       
        #     FFTSHIFT=fftshift(ABSFFT)       
        #     FFTSCN=np.minimum((np.around((63*FFTSHIFT)/(1.6e5)))+ 1 , 64)
        #     if(sum(Idet)>=5):            
        #         #Plot.ax[1].plot(Rbin[cls.Idet.index(1)],cls.iterator-1,color='b',marker='.')    
        #         # queue.put([scan,Rbin[cls.Idet.index(1)],cls.iterator-1])     
        #         queue.put([self.dataScan,FFTSCN,Rbin[Idet.index(1)],DataScan.rangeIterator-1])
        #     else:
        #         queue.put([self.dataScan,FFTSCN,None,None])
        #     # DataScan.multiDataScan=[]
        #     DataScan.multiIQScan=[]
        #     DataScan.fftIterator=0
             
            # i=0

        # x=c.processInfo(info)
        # for i in range(self.numSamplesTotal):
        #     print(x[i])
        # time.sleep(10)
        # while (i.value<self.numSamplesTotal):                               
        #     self.dataScan.append(c.processInfo(info)[i.value])
        #     i.value=i.value+1 

       
        #self.fullWaveData=self.fullWaveData-np.mean(self.fullWaveData)
            
    #def processMultiImgScan(self,cls):
        # if cls.iterator % NFFT == 0: #gather scans for FFT
        #     cls.multiScans=[]
        #print(cls.process)
        # if cls.process==Config.Process.VELOCITY or cls.process==Config.Process.ALL:
        #     self.generateFFTScan(cls)# generate fft for each full wave independently
        #if cls.process==Config.Process.RANGE_DETECTION or cls.process==Config.Process.ALL:
        #RangeDetection.generateEnvScan(self) # 
        
        
    # def generateEnvScan(self,cls):
    #     if cls.iterator == 0:
    #         cls.iterator+= 1
    #         return
    #     scanEnv=enveloppe((np.array(self.dataScan) - self.prevDataScan))
    #     #outputCsv(data=scanEnv,mode="w")
    #     # if cls.iterator==1:
    #         #print(scanEnv)
    #         #time.sleep(10)
    #     cls.scanEnvProcessed.append(np.minimum((np.around((63*(scanEnv))/(10e3)))+ 1 , 64)) # appended just for the print
    #     self.Idet= [value>=10 for value in cls.scanEnvProcessed[cls.iterator-1]] # need to be changed to self.scanEnv in the future ( no need to append data)
    #     #outputCsv(data=self.Idet,mode="w")
    #     cls.iterator=cls.iterator+1
    #     if cls.plot==Config.Plot.RANGE_DETECTION or cls.plot==Config.Plot.ALL:            
    #         self.plotRangeDetection(cls)

    # def generateFFTScan(self,cls): 
    #     self.FFTData=hilbert_from_scratch(np.array(self.dataScan))       
    #     cls.multiScans.append(self.FFTData)
        
    # @classmethod
    # def processScanFFT(cls):
    #     cls.multiScans=np.transpose(np.array(cls.multiScans))                  
    #     FFT=fft(cls.multiScans,n=Config.NFFT,axis=1) #NFFT=32       
    #     ABSFFT=np.absolute(FFT)      
    #     ABSFFT[:,0]=0       
    #     FFTSHIFT=fftshift(ABSFFT)       
    #     cls.FFTSCN=np.minimum((np.around((63*FFTSHIFT)/(1.6e5)))+ 1 , 64)
    #     cls.multiScans=[]
    #     if cls.plot==Config.Plot.VELOCITY or cls.plot==Config.Plot.ALL:            
    #         cls.plotVelocity()

    # #@classmethod
    # def plotRangeDetection(self,cls):      
    #     #plt.imshow(cls.scanEnvProcessed,aspect="auto",cmap='viridis',extent=[1,20,0,100])        
    #     if(sum(self.Idet)>=10):
    #         plt.plot(Rbin[self.Idet.index(1)],cls.iterator-1,color='b',marker='.')
        
    #     plt.pause(0.0001)
    #     #plt.clf()
    # @classmethod
    # def plotVelocity(cls):        
    #     plt.imshow(cls.FFTSCN,extent=[-40,37.5,1,5.5],aspect="auto",cmap='viridis',vmin=1,vmax=64)
    #     plt.pause(0.0001)
    #     #plt.clf()




     # unused data
       
    # self.msgType=info.msg.scanInfo.msgType
    # self.sourceId=info.msg.scanInfo.sourceId
    # self.msgId=info.msg.scanInfo.msgId    
    # self.channelRiseTime=info.msg.scanInfo.channelRiseTime
    # self.scanSNRLinear=info.msg.scanInfo.scanSNRLinear
    # self.ledIndex=info.msg.scanInfo.ledIndex
    # self.lockspotOffset=info.msg.scanInfo.lockspotOffset
    # self.scanStartPs=info.msg.scanInfo.scanStartPs
    # self.scanStepBins=info.msg.scanInfo.scanStepBins
    # self.scanStopPs=info.msg.scanInfo.scanStopPs
    # self.scanFiltering=info.msg.scanInfo.scanFiltering
    # self.reserved=info.msg.scanInfo.reserved
    # self.antennaId=info.msg.scanInfo.antennaId
    # self.operationMode=info.msg.scanInfo.operationMode
    # self.numSamplesInMessage=info.msg.scanInfo.numSamplesInMessage
    
    # self.messageIndex=info.msg.scanInfo.messageIndex
    # self.numMessagesTotal=info.msg.scanInfo.numMessagesTotal


    
            # """_______________std deviation______________"""
            # squaredSum= (np.sum(np.square((self.scanDataBox[:,i]) -average)))/DataScan.windowSize  # sum Xi²/n  of the last scans on one bin (X = scan)
            # stdDeviation= np.sqrt(squaredSum)/np.sqrt(DataScan.windowSize) # standard deviation
            # # self.stdArray.append(stdDeviation)
  
            
            
            #     self.detectionArray[i] = abs(self.enveloppe[i]-average ) > stdDeviation* DataScan.thresholdMult
               
            # print("squared sum : ",squaredSum)

            # self.detectionArray[i] = (abs(self.enveloppe[i]-average)/ stdDeviation) > 7
            

            #"""_______________median deviation______________"""
            # medData=np.median(self.scanDataBox[:,i])
            # deviation=abs(self.scanDataBox[:,i]-medData)            
            # mad=np.median(deviation)
            # self.detectionArray[i] = (abs(self.enveloppe[i]-average) ) > mad * DataScan.thresholdMult
            

            #"""_______________mode deviation______________"""
            # modeData = mode(self.scanDataBox[:,i])
            # mad=(np.abs(self.scanDataBox[:,i] - modeData).sum())/DataScan.windowSize 
            # self.detectionArray[i] = (abs(self.enveloppe[i]-average) ) > mad * DataScan.thresholdMult
            
            #"""_____________________________"""

            # self.detectionArray[i] = (abs(self.enveloppe[i]-average) ) > abs(average*DataScan.thresholdMult)
           
        # print(time.perf_counter()- t1 )