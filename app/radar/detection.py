
from .dataProcessing import *
import numpy as np
import math

class Detection:  
    """ 
    This detection algorithm is exlained in the MRM RET User Guide <<Appendix A: MRM Server Filters>> page 26
    The code here doesn't give the exact same results as the one used in in the MRM Service 
    ( when a bin is marked as detected, this algorithm tends to ignore that bin faster compared to 
    the mrm service one), prolly the code (filtering) used in the service isnt exactly the same described in the 
    documentation .

    this can be improved with the right filtering (especially the motion Filter which tends to ignore speed above 5-7-10 hz of doppler shift depending on the fir filter used, given the sampling frequency is at 40Hz in slow time)
    in the end this algorithm works and gives accurate detections nonetheless.

    3 filters are used with a cut off frequency calculated with scipy.freqz given sampling 
    frequency equals 4 x F0 (double nyquist frequency mentionned in documentation) 4.3GHz x 4 = 17.2 Ghz  :
    
    * band pass filter: on each signal (fast time filtering)
    
    ** motion filter : filtering the 4 newest signals on each bin "vertically" ( filtering on slow time)
    
    *** detection filter: a high pass filter: this filter is used on the I and Q signals to form the envelope, 
    that will be used for detections.

    3 parameters can be changed for detection:
    windowSize, thresholdMult and adjacentDetectionCondition,
    # NOTE : adjacentDetectionCondition isn't the same as the one as used in the MRM Service
    for the adjacentDetectionCondition the default value being at 6 , it takes the 6 adjacent values of the detection array( by convolution ), 
    if the number of detection is equals of greater than (adjacentDetectionCondition / 2 + 1 which is equal to 4) then that bin is marked as detection

    When save process/save detections is checked: the program will split detections in 2 classes, detection and no detections splitting them into segments
    of size numberOfSamplesTaken segment= [ index_of_detection, index_of_bin_detection, 100_values_of_bandpass_filtered_signed_after_bin_detection]  

    """

    #detection
    iteratorDataScan=0
    windowSize=100
    window=np.ones(windowSize)/windowSize
    startFilter=False
    initDataBox=False
    isDetectionBoxFull=False
    thresholdMult=3
    adjacentDetectionCondition = 6
    numberOfSamplesTaken=100
    detIterator=0
    detectionChecker=np.ones(adjacentDetectionCondition)

    csvDetectionSamples=[]
    csvNoDetectionSamples=[]
    
    init = False
    sin=[]
    cos=[]

    @staticmethod
    def filterData(dataScan):
        dataScan.bpFiltered=Filter.bandpass_filter(dataScan.dataScan)
        # Filter.appendData(dataScan.bpFiltered)
        if Detection.iteratorDataScan  > 4 or Detection.startFilter:
            dataScan.mtFiltered = Filter.motionFiltered()
            Detection.startFilter=True
            Detection.detectionFiltered(dataScan)

    @staticmethod
    def appendEnvelopeToDataBox(dataScan):
        #create scanDataBox (multi scan data envelope) for detection
        if not Detection.initDataBox:
            Detection.scanDataBox=np.zeros((Detection.windowSize,dataScan.numSamplesTotal))            
            Detection.initDataBox= True

        #insert dataScan in the scanDataBox
        if Detection.startFilter:
            Detection.scanDataBox[Detection.iteratorDataScan]= np.array(dataScan.enveloppe)
            
            if Detection.iteratorDataScan >= Detection.windowSize - 1:
                Detection.iteratorDataScan = 0

    @classmethod
    def detectionFiltered(cls,dataScan):
        if not cls.init:
            max=(dataScan.numSamplesTotal)*61*10**(-12)
            Tbin= np.arange(0,max,61*10**(-12))
            F0=4.3*10**9
            
            for t in Tbin:
                cls.sin.append(2*math.pi*math.sin(F0*t))
                cls.cos.append(2*math.pi*math.cos(F0*t))
            cls.init= True
   
        Q=np.array(dataScan.mtFiltered)*cls.sin
        I=np.array(dataScan.mtFiltered)*cls.cos
        Q_filtered=Filter.detection_lowpass_filter(Q)
        I_filtered=Filter.detection_lowpass_filter(I)    

        IQ_Filtred=I_filtered + Q_filtered *1j
        dataScan.enveloppe=np.abs(IQ_Filtred)


    @staticmethod
    def calculateDetection(dataScan):
       
        for i in range(dataScan.numSamplesTotal):
            
            average=(Detection.scanDataBox[:,i].sum())/Detection.windowSize # average of last scans on one bin
            # stdDeviation=np.std(Detection.scanDataBox[:,i])
            squaredSum= np.sum(np.square(Detection.scanDataBox[:,i]))/Detection.windowSize  # sum Xi²/n  of the last scans on one bin (X = scan)
            # print("size :   ",Detection.scanDataBox.shape)
            stdDeviation= np.sqrt(squaredSum-np.square(average)) # standard deviation
            dataScan.detectionArray[i] = abs(dataScan.enveloppe[i]-average ) > Detection.thresholdMult * stdDeviation
        
        dataScan.detectionFinal = np.convolve(Detection.detectionChecker,dataScan.detectionArray)
        dataScan.condition = dataScan.detectionFinal > int(Detection.adjacentDetectionCondition/2)+1
        dataScan.indices = np.where(dataScan.condition)        
        
        if dataScan.config.processSaveDetection:
            Detection.appendDetectionToCsv(dataScan)
        Detection.detIterator+=1

    
    # code for taking samples before and after detection ( centering the detection )
    # @staticmethod
    # def appendDetectionToCsv(dataScan):
    #     # Detection Slice
    #     if dataScan.indices[0].size == 0:
    #         return
    #     indice=dataScan.indices[0][0] - Detection.numberOfSamplesTaken/2
    #     if indice <=0 :
    #         return
    #     if (indice+ Detection.numberOfSamplesTaken) < (dataScan.numSamplesTotal -1):
    #         Detection.csvDetectionSamples.append([Detection.detIterator,indice,*dataScan.bpFiltered[indice:(indice+Detection.numberOfSamplesTaken)]])
       
    #         # No detections Segments
    #         numOfSegmentsBeforeDetection = int(indice/Detection.numberOfSamplesTaken)
    #         numOfSegmentsAfterDetection = int((dataScan.numSamplesTotal-(indice + Detection.numberOfSamplesTaken))/Detection.numberOfSamplesTaken)
        
    #         while numOfSegmentsBeforeDetection != 0:
    #             Detection.csvNoDetectionSamples.append([Detection.detIterator,indice,*dataScan.bpFiltered[indice - numOfSegmentsBeforeDetection*Detection.numberOfSamplesTaken : indice - \
    #                                             numOfSegmentsBeforeDetection*Detection.numberOfSamplesTaken + Detection.numberOfSamplesTaken]])
    #             numOfSegmentsBeforeDetection -= 1
        
    #         for i in range(1 ,numOfSegmentsAfterDetection + 1):
    #             Detection.csvNoDetectionSamples.append([Detection.detIterator,indice,*dataScan.bpFiltered[indice+Detection.numberOfSamplesTaken*i :indice+ \
    #                                                             Detection.numberOfSamplesTaken*i +Detection.numberOfSamplesTaken]])

    #taking samples after detection
    @staticmethod
    def appendDetectionToCsv(dataScan):
        # Detection Slice
        if dataScan.indices[0].size == 0:
            return
        
        if (dataScan.indices[0][0] + Detection.numberOfSamplesTaken) < (dataScan.numSamplesTotal -1):
            Detection.csvDetectionSamples.append([Detection.detIterator,dataScan.indices[0][0],*dataScan.bpFiltered[dataScan.indices[0][0]:(dataScan.indices[0][0]+Detection.numberOfSamplesTaken)]])       
        
            # No detections Segments
            numOfSegmentsBeforeDetection = int(dataScan.indices[0][0]/Detection.numberOfSamplesTaken)
            numOfSegmentsAfterDetection = int((dataScan.numSamplesTotal-(dataScan.indices[0][0] + Detection.numberOfSamplesTaken))/Detection.numberOfSamplesTaken)
        
            while numOfSegmentsBeforeDetection != 0:
                Detection.csvNoDetectionSamples.append([Detection.detIterator,dataScan.indices[0][0],*dataScan.bpFiltered[dataScan.indices[0][0] - numOfSegmentsBeforeDetection*Detection.numberOfSamplesTaken : dataScan.indices[0][0] - \
                                                numOfSegmentsBeforeDetection*Detection.numberOfSamplesTaken + Detection.numberOfSamplesTaken]])
                numOfSegmentsBeforeDetection -= 1
        
            for i in range(1 ,numOfSegmentsAfterDetection + 1):
                Detection.csvNoDetectionSamples.append([Detection.detIterator,dataScan.indices[0][0],*dataScan.bpFiltered[dataScan.indices[0][0]+Detection.numberOfSamplesTaken*i :dataScan.indices[0][0]+ \
                                                                Detection.numberOfSamplesTaken*i +Detection.numberOfSamplesTaken]])