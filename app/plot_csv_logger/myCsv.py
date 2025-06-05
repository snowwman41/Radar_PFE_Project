import os
import csv

import numpy as np
import time
from common.enums import FileType,DataMode
from config.config import Config  
import json
from enum import Enum

class MyCsv:
    files={}

    folderName=None
    folderPrefix="outputFolders/dataAcquisition_"
    
    def __init__(self,config):
        self.config = config
        self.multiScanInfo=[]

        if self.config.postProcessing ==-1 and self.config.plotSaveRaw!= DataMode.SAVE and self.config.plotSaveDoppler!= DataMode.SAVE and self.config.plotSaveDetection != DataMode.SAVE and self.config.cameraSave != DataMode.SAVE:
                return
        if self.config.plotSaveRaw == DataMode.SAVE:
            MyCsv.files[FileType.SCAN]=["System timestamp","Timestamp","DataScan"]

        if self.config.plotSaveDoppler == DataMode.SAVE:
            MyCsv.files[FileType.FFT]=None

        if self.config.processSaveDetection:
            MyCsv.files[FileType.DETECTION]=None
            MyCsv.files[FileType.NODETECTION]=None
            
        if self.config.cameraSave == DataMode.SAVE:
            MyCsv.files[FileType.CAMERA]=["System Timestamp","Camera Timestamp"]
        
        
        if self.config.postProcessing ==-1:
            self.checkExistingFolder()
            self.initFiles()

        else:
            self.folderName=f"{self.folderPrefix}{self.config.postProcessing}"
            self.initFiles()
            self.setScanData()
        
    def getConfig(self):
        with open(f"{self.folderName}/config.json","r") as file:
            jsonConfig=file.read()
        config = Config(**json.loads(jsonConfig))
        config.Rbin=json.loads(jsonConfig)["Rbin"]
        config.postProcessing = self.config.postProcessing
        config.plotSaveRaw = DataMode.PLOT
        config.plotSaveDetection= DataMode.PLOT
        config.plotSaveDoppler= DataMode.PLOT
        config.cameraSave= DataMode.PLOT
        config.processDetection = True
        config.processDoppler=True
        config.plot= 3
        config.processSaveDetection=self.config.processSaveDetection
        self.config= config

        return self.config
    # @classmethod
    # def initialize(cls,config : Config,savePathSend):
    #     cls.config=config
    #     # if cls.config.postProcessing:
    #     #     cls.folderName=f"{cls.folderPrefix}{cls.config.postProcessing}"
    #     #     cls.setScanData()
    #     #     return
    #     # if cls.config.saveData==0:
    #     #     return
    #     cls.checkExistingFolder(savePathSend)
    #     MyCsv.initFiles()
    
     
    def setScanData(self):

        with open(f"{self.folderPrefix}{self.config.postProcessing}/SCAN.csv") as file:
            reader=csv.reader(file)
            first=True
            for row in reader:
                if first :
                    first = False
                    continue
                self.multiScanInfo.append(np.array(row[0].split(";"),dtype=np.int32))

    def checkExistingFolder(self):
        i=0     
        if not os.path.exists(os.path.dirname(os.path.dirname(os.path.abspath(__file__))).__add__("/outputFolders")):
            os.makedirs(os.path.dirname(os.path.dirname(os.path.abspath(__file__))).__add__("/outputFolders"),exist_ok=True)
        while True:           

            if os.path.exists(f"{self.folderPrefix}{i}"):
                i+=1
            else:
                self.folderName=f"{self.folderPrefix}{i}"
                os.mkdir(f"{self.folderName}")
                break
        # savePathSend.send(cls.folderName)        
       
          
    def initFiles(self):
        if self.config.postProcessing ==-1:
            with open(f"{self.folderName}/config.json","w") as f:
                json.dump(self.config.__dict__, f,cls=JsonEncoder, indent=4)        
        for type,header in self.files.items():
            setattr(self, type.name, f"{self.folderName}/{type.name}.csv" ) # to set fullNameVariables as class variables            
            with open (f"{self.folderName}/{type.name}.csv" ,"w",newline="") as f:
                writer = csv.writer(f ,delimiter=";")
                if header is not None:
                    writer.writerow(header)                
    
    def outputCsv(self,file,data):   

        if file == FileType.SCAN :           
            with open (f"{self.SCAN}","a",newline="") as f:            
                for row in data:
                    writer = csv.writer(f,delimiter=";")                 
                    writer.writerow(row)

        if file == FileType.DETECTION :  
            with open (f"{self.DETECTION}","a",newline="") as f:        
                writer = csv.writer(f,delimiter=";")  
                for row in data:
                    writer.writerow(row) 
         
        if file == FileType.NODETECTION :  
            with open (f"{self.NODETECTION}","a",newline="") as f:        
                writer = csv.writer(f,delimiter=";")  
                for row in data:  
                    writer.writerow(row)          

        if file == FileType.FFT   :
            with open (f"{self.FFT}","a",newline="") as f:
                if self.config.plotSaveDoppler == DataMode.SAVE:
                    writer = csv.writer(f,delimiter=";") 
        
                    for row in data:                                  
                        for column in row:  
                            writer.writerow(column)  
        if file == FileType.CAMERA   :
            with open (f"{self.CAMERA}","a",newline="") as f:
                # if cls.config.plotSaveDoppler == DataMode.SAVE:
                writer = csv.writer(f,delimiter=";") 
                for row in data:         
                    writer.writerow(row)            
                    # writer.writerow(row[2:])
# MyCsv.outputCsv(FileType.DETECTION,[["dataScan",*dataScanObj.dataScan],["prevDataScan",*dataScanObj.prevDataScan],["ScanEnveloppe (filtered)",*scanEnv.tolist()],["scanEnveloppeProcessed",*scanEnveloppeProcessed],["detection",*cls.Idet]])   
# MyCsv.outputCsv(FileType.DETECTION,[["dataScan",*dataScanObj.dataScan],["prevDataScan",*dataScanObj.prevDataScan],["ScanEnveloppe (filtered)",*scanEnv.tolist()],["scanEnveloppeProcessed",*scanEnveloppeProcessed]])   

class JsonEncoder(json.JSONEncoder):
    def default(self,obj):
        if isinstance(obj,Enum):
                return obj.name
        else :
                return obj