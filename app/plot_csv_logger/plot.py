from common.enums import DataMode

from matplotlib import pyplot as plt
import numpy as np

class Plot():    
    fig=ax=None
    detectionIterator=0
    @classmethod
    def initialize(cls,radarQueue,stopRec,config):
               
        if config.plot:
            cls.fig,cls.ax=plt.subplots(ncols=config.plot,nrows=1)
          
        while True:
            
            if stopRec.poll() :  
                plt.close() 

            print("Queue Size : ",radarQueue.qsize())

            #to plot the most recent frames
            while (radarQueue.qsize()>1):
                radarQueue.get() 

            radarData=radarQueue.get()  
            Plot.detectionIterator+=1

            #type error for when there is only one plot
            if config.plotSaveRaw == DataMode.PLOT and radarData["dataScan"] is not None:                
                try:
                    ax=cls.ax[config.plot - 1]
                    ax.cla() 
                    ax.plot(config.Rbin,radarData["dataScan"],color='b')  
                    ax.set_title("Données Brutes RADAR")
                    ax.set_xlabel("Distance (m)")
                    ax.set_ylabel("Amplitude")    
   
                except TypeError:
                    cls.ax.cla()                
                    cls.ax.plot(config.Rbin,radarData["dataScan"],color='b')  
                    cls.ax.set_title("Données Brutes RADAR")
                    cls.ax.set_xlabel("Distance (m)")
                    cls.ax.set_ylabel("Amplitude")
                     
            if config.plotSaveDetection == DataMode.PLOT and (radarData.get("detectionIndices") is not None and radarData.get("detectionArray") is not None):                    
              
                try:
                    # 200 detection point to reset the detection plot otherwise it will become slow to update,
                    ax=cls.ax[config.plot - 2 if config.plot !=2 else 0 if config.plotSaveRaw == DataMode.PLOT else 1]
                    if Plot.detectionIterator > 200:                       
                        ax.cla()
                        Plot.detectionIterator=0
                    if len(radarData["detectionIndices"][0])>0:                
                        ax.scatter(np.array(config.Rbin)[radarData.get("detectionIndices")[0][0]],Plot.detectionIterator,color='black')   
                        ax.set_title("Detections")
                        ax.set_xlabel("Distance (m)")
                        ax.set_ylabel("Echantillons")
            
                except TypeError:  
                    if Plot.detectionIterator > 200:
                        cls.ax.cla()
                        Plot.detectionIterator=0
                        
                    if len(radarData[1][0])>0 :                         
                        cls.ax.scatter(np.array(config.Rbin)[radarData.get("detectionIndices")[0][0]],Plot.detectionIterator,color='black') 
                        cls.ax.set_title("Detections")
                        cls.ax.set_xlabel("Distance (m)")
                        cls.ax.set_ylabel("Echantillons")
                        
            if config.plotSaveDoppler == DataMode.PLOT and radarData.get("doppler") is not None:
                try:     
                    ax=cls.ax[config.plot - 3 if config.plot !=2 else 0 if config.plotSaveRaw == DataMode.PLOT else 0]           
                    ax.cla()
                    ax.imshow(radarData.get("doppler") ,extent=[-1*config.maxSpeed,config.maxSpeed,config.R2,config.R1],aspect="auto")  
                    ax.set_title("Doppler")
                    ax.set_xlabel("Vitesse km/H")
                    ax.set_ylabel("Distance (m)")
                except TypeError:
                    cls.ax.cla()
                    cls.ax.imshow(radarData.get("doppler") ,extent=[-1*config.maxSpeed,config.maxSpeed,config.R2,config.R1],aspect="auto")   
                    cls.ax.set_title("Doppler")
                    cls.ax.set_xlabel("Vitesse km/H")
                    cls.ax.set_ylabel("Distance (m)")
            plt.tight_layout()
            plt.pause(0.00001) 
            
       
        plt.close() 
              
           
