from common.enums import DataMode
import math
import shutil

class Config:
    #ipAdress=scanInterval=NFFT=timeout=processVelocity=processRange=plotVelocity=plotRange,plotScan=None
    
    def __init__(self,*,R1,R2,ipAdress,scanInterval,userBaseII,userTxGain,scanPerControl,plotSaveRaw,processDoppler,plotSaveDoppler,\
                 timeout,camOn,cameraSave,camSaveQuality,scanResolutionBins=32,NFFT,**kwargs):        
    
        T1, T2, R1, R2, Rbin, Nbin = Config.radarScanSetup(R1,R2,scanResolutionBins) # specify wanted range to calculate required start and stop scan times

        #radar config
        self.ipAdress=ipAdress
        self.scanInterval=scanInterval # scan interval between scans us
        self.userBaseII = userBaseII # integration index, "log2 of the number of integrations, 7 => 2^7 = 128 integrations"
        self.userScanStart = int(T1*1000) # start scan after the impulse
        self.userScanStop = int(T2*1000) # stop scan after the impulse
        self.userTxGain = userTxGain #transmit power 0 lowest,63 highest
        self.scanPerControl=scanPerControl  #number of scans by one control request 65535 = run forever (infinite number of scans)
        self.Rbin=Rbin # range between 2 samples in one scan wave
        self.R1=R1
        self.R2=R2
        self.timeout=timeout # communication timeout 
        self.scanResolutionBins=scanResolutionBins

        #radar
        self.NFFT = NFFT
        self.processDoppler=processDoppler
        self.plotSaveRaw=plotSaveRaw
        self.plotSaveDoppler=plotSaveDoppler
        if self.processDoppler == False:
            self.plotSaveDoppler= DataMode.NONE

        #cam
        self.camOn=camOn
        self.cameraSave=cameraSave
        self.camSaveQuality=camSaveQuality* 10
        
        total, used, free = shutil.disk_usage("/")
        #convert bytes to GB, if it's less than 1 gb stop saving
        if free/2**30 < 1:
            self.plotSaveRaw=DataMode.NONE
            self.plotSaveDoppler=DataMode.NONE
            self.cameraSave = DataMode.NONE

        # self.saveData= self.plotSaveRaw == DataMode.SAVE or self.plotSaveDetection == DataMode.SAVE or self.plotSaveDoppler== DataMode.SAVE or cameraSave==DataMode.SAVE

        F0= 4.3 * 10**9 # frequency of the radar 4.3 Ghz 
        c=3*10**8 # speed of light
        waveLength = c/F0
        
        #max speed is calculated on half the wave length of the radar speed = distance/time ; distance = waveLength/2 , time = PRI
        self.maxSpeed = ((waveLength/2)/self.scanInterval)*3600*1000 # km/s

    
    @staticmethod        
    def radarScanSetup(R1, R2,scanResolutionBins):
        # Speed of light.
        c = 0.29979  # m/ns

        # Radio parameters.
        dTmin = 1/(512*1.024)  # ns
        Tbin = scanResolutionBins*dTmin  # ns
        dNbin = 96  # number of bins in a scan segment
        dT0 = 10  # ns 

        # delay to send radar waves
        # NOTE: This is the empirically measured value with broadspec antennas
        # connected directly on SMA connectors as provide in the kit. Alternate
        # antenna connections and/or cable lengths require a different value.

        # Calculation of T1 and T2 subject to radio timing.
        T1 = 2*R1/c + dT0  # ns
        T2 = 2*R2/c + dT0  # ns

        Nbin = (T2 - T1)/Tbin
        Nseg = math.ceil(Nbin/dNbin)
        Nbin = dNbin*Nseg

        T1 = math.floor(1000*dTmin*math.floor(T1/dTmin))/1000  # ns
        T2 = Nbin*Tbin + T1  # ns
        T2 = math.floor(1000*dTmin*math.ceil(T2/dTmin))/1000  # ns

        # Recompute R1 and R2 using T1 and T2.
        R1 = c*(T1 - dT0)/2
        R2 = c*(T2 - dT0)/2

        dRbin = c*Tbin/2  # m
        Rbin = [R1 + dRbin*i for i in range(int(Nbin))]  # m

        return T1, T2, R1, R2, Rbin, Nbin  


        
        
        


        