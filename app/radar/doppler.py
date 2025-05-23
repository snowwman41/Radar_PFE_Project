from plot_csv_logger.myCsv import *
from scipy.fftpack import *
import numpy as np

class Doppler:
    multiIQScan=[]        
    fftCsv=[]
    init = False

    @staticmethod
    def IQTransform(dataScan):
        #hilbert method to get the analytical signal
        dopplerIQ=hilbert(np.array(dataScan.dataScan))
        return dopplerIQ

    @classmethod
    def processFFT(cls,dataScan):

        if cls.config.processDoppler:   
            multiIQScanT=np.transpose(cls.multiIQScan)
            cls.multiIQScan=[]        
            FFT=fft(multiIQScanT,n=cls.config.NFFT)
            ABSFFT=np.absolute(FFT)        
            ABSFFT[:,0]=0      
            FFTSHIFT=fftshift(ABSFFT,axes=1)
            if cls.config.plotSaveDoppler == DataMode.SAVE:
                cls.fftCsv.append(FFTSHIFT)
            dataScan.FFTSCN=np.minimum((np.around((63*FFTSHIFT)/(1.6e5)))+ 1 , 64)  

        

    