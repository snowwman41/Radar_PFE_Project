from common.enums import FileType,DataMode
from config.config import Config  
from enum import Enum

import os
import csv
import json

class MyCsv:
    files={}

    folderName=None
    folderPrefix="outputFolders/dataAcquisition_"
    
    def __init__(self,config):
        self.config = config

        if self.config.plotSaveRaw!= DataMode.SAVE and self.config.plotSaveDoppler!= DataMode.SAVE and self.config.cameraSave != DataMode.SAVE:
                return
        if self.config.plotSaveRaw == DataMode.SAVE:
            MyCsv.files[FileType.SCAN]=["System timestamp","Timestamp","DataScan"]

        if self.config.plotSaveDoppler == DataMode.SAVE:
            MyCsv.files[FileType.FFT]=None

        if self.config.cameraSave == DataMode.SAVE:
            MyCsv.files[FileType.CAMERA]=["System Timestamp","Camera Timestamp"]        
              
        self.checkExistingFolder()
        self.initFiles()
    
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
          
    def initFiles(self):
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

class JsonEncoder(json.JSONEncoder):
    def default(self,obj):
        if isinstance(obj,Enum):
                return obj.name
        else :
                return obj