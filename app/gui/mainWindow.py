from multiprocessing import Process
import sys

from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt,QCoreApplication
from PyQt5.QtGui import QIntValidator,QDoubleValidator,QFont

from config.config import Config
from common.enums import DataMode,OutputType

class MainWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()
        
        self.labelFont=QFont()
        self.labelFont.setBold(True)
        self.labelFont.setUnderline(True)

        self.mainLayout=QVBoxLayout()            
  
        #radar
        self.initRadarLayout() 
        #camera
        self.initCameraLayout()
        # parameters
        self.initParametersLayout()    
        #controlButtons 
        self.initControlButtonsLayout()

        self.mainLayout.addLayout(self.radarLayout)
        self.mainLayout.addLayout(self.cameraLayout)
        self.mainLayout.addLayout(self.parametersLayout)
        self.mainLayout.addLayout(self.buttonsLayout)
        
        # self.initDefaultValues()
        container = QWidget()
        container.setLayout(self.mainLayout)
        
        self.setCentralWidget(container)
        self.setGeometry(100,100,420,400)
        self.setFixedSize(self.size())

    def initControlButtonsLayout(self):

        self.buttonsLayout= QHBoxLayout()
        self.startButton = QPushButton("Start")
        self.stopButton =  QPushButton("Stop") 

        self.buttonsLayout.addWidget(self.startButton)
        self.buttonsLayout.addWidget(self.stopButton)        
        
    def initRadarLayout(self):
        
        self.radarLayout=QVBoxLayout()         

        #raw
        self.rawLayout=QHBoxLayout()
        self.rawRadioGroup=QButtonGroup(self) 
        self.radarLabel=QLabel("Radar")
        
        self.radarLabel.setSizePolicy(50,50)
        self.radarLabel.setFont(self.labelFont)        
        self.rawCheckbox=QCheckBox("Raw")
        self.noneRawRadio=QRadioButton("None")
        self.plotRawRadio=QRadioButton("Plot")
        self.saveRawRadio=QRadioButton("Save Data")    
        self.rawRadioGroup.addButton(self.noneRawRadio)   
        self.rawRadioGroup.addButton(self.plotRawRadio)     
        self.rawRadioGroup.addButton(self.saveRawRadio) 
            
        self.rawLayout.addWidget(self.rawCheckbox)
        self.rawLayout.addWidget(self.noneRawRadio)
        self.rawLayout.addWidget(self.plotRawRadio)
        self.rawLayout.addWidget(self.saveRawRadio)

        #doppler
        self.dopplerLayout=QHBoxLayout()
        self.dopplerRadioGroup=QButtonGroup(self)
        self.dopplerCheckbox=QCheckBox("Doppler")
        self.noneDopplerRadio=QRadioButton("None")
        self.plotDopplerRadio=QRadioButton("Plot")
        self.saveDopplerRadio=QRadioButton("Save Data")  
        self.dopplerRadioGroup.addButton(self.noneDopplerRadio) 
        self.dopplerRadioGroup.addButton(self.plotDopplerRadio)     
        self.dopplerRadioGroup.addButton(self.saveDopplerRadio)

        self.dopplerLayout.addWidget(self.dopplerCheckbox)
        self.dopplerLayout.addWidget(self.noneDopplerRadio)
        self.dopplerLayout.addWidget(self.plotDopplerRadio)   
        self.dopplerLayout.addWidget(self.saveDopplerRadio)            

        #detection
        self.detectionLayout=QHBoxLayout()
        self.detectionRadioGroup=QButtonGroup(self)
        self.detectionCheckbox=QCheckBox("Detection")   
        self.noneDetectionRadio=QRadioButton("None")   
        self.plotDetectionRadio=QRadioButton("Plot")
        self.saveDetectionRadio=QRadioButton("Save Data")
        self.detectionRadioGroup.addButton(self.noneDetectionRadio)
        self.detectionRadioGroup.addButton(self.plotDetectionRadio)
        self.detectionRadioGroup.addButton(self.saveDetectionRadio)        

        self.detectionLayout.addWidget(self.detectionCheckbox)
        self.detectionLayout.addWidget(self.noneDetectionRadio)
        self.detectionLayout.addWidget(self.plotDetectionRadio)
        self.detectionLayout.addWidget(self.saveDetectionRadio)        
        
        #radar layout
        self.radarLayout.addWidget(self.radarLabel)
        self.radarLayout.addLayout(self.rawLayout)
        self.radarLayout.addLayout(self.dopplerLayout)
        self.radarLayout.addLayout(self.detectionLayout)

    def initCameraLayout(self):
        
        self.cameraLayout=QVBoxLayout()  

        self.cameraLabel=QLabel("Camera")
        self.cameraLabel.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
        self.cameraLabel.setFont(self.labelFont)
        self.cameraHorizontalLayout=QHBoxLayout()

        #radioButtons for camera
        self.cameraCheckbox=QCheckBox("camOn")
        self.cameraRadioGroup=QButtonGroup()      
        self.noneCameraRadio=QRadioButton("None")   
        self.captureCameraRadio=QRadioButton("Capture")
        self.saveCameraRadio=QRadioButton("Save Images")     
        self.cameraRadioGroup.addButton(self.noneCameraRadio)
        self.cameraRadioGroup.addButton(self.captureCameraRadio)
        self.cameraRadioGroup.addButton(self.saveCameraRadio)      

        #cam quality slider
        self.cameraQualityLabel=QLabel("saved images quality")  
        self.cameraQualitySlider=QSlider(Qt.Orientation.Horizontal)
        self.cameraQualitySlider.setRange(1,10)        
         
        self.cameraQualitySlider.setMaximumWidth(100)
        self.cameraQualitySlider.setPageStep(1)
        self.cameraQualitySlider.setTickInterval(1) 

        #camera layout
        self.cameraLayout.addWidget(self.cameraLabel)
        self.cameraHorizontalLayout.addWidget(self.cameraCheckbox)
        self.cameraHorizontalLayout.addWidget(self.noneCameraRadio)
        self.cameraHorizontalLayout.addWidget(self.captureCameraRadio)
        self.cameraHorizontalLayout.addWidget(self.saveCameraRadio)
        self.cameraLayout.addLayout(self.cameraHorizontalLayout)
        self.cameraLayout.addWidget(self.cameraQualityLabel,Qt.AlignRight)        
        self.cameraLayout.addWidget(self.cameraQualitySlider,Qt.AlignRight)        

        #init radio buttons object names        
        self.noneCameraRadio.objectName=self.noneRawRadio.objectName=self.noneDopplerRadio.objectName=self.noneDetectionRadio.objectName=DataMode.NONE
        self.captureCameraRadio.objectName=self.plotRawRadio.objectName=self.plotDopplerRadio.objectName=self.plotDetectionRadio.objectName=DataMode.PLOT
        self.saveCameraRadio.objectName=self.saveRawRadio.objectName=self.saveDopplerRadio.objectName=self.saveDetectionRadio.objectName=DataMode.SAVE
    
        #init checkbox object names
        self.rawCheckbox.objectName=OutputType.RAW
        self.detectionCheckbox.objectName=OutputType.DETECTION
        self.dopplerCheckbox.objectName=OutputType.DOPPLER
        self.cameraCheckbox.objectName=OutputType.CAMERA


    def initParametersLayout(self):
        
        self.parametersLayout=QVBoxLayout()   
          
        self.grid=QGridLayout()
        
        self.parametersLabel=QLabel("Parameters")
        self.parametersLabel.setFont(self.labelFont)
        self.parametersLayout.addWidget(self.parametersLabel)
        self.parametersLayout.addLayout(self.grid)

        self.textInputs={"scanInterval":25000,
                    "R1":1,
                    "BII":10,
                    "R2":20,        
                    "NFFT":11,
                    "postProcessIndex":""
                    } 
        for index,(textInput,initValue) in enumerate(self.textInputs.items()):
            MainWindow.initTextInput(self,textInput,initValue,index)
        self.postProcessIndexInput.textChanged.connect(self.postProcessIndexInputOnChange)
        self.postProcessIndex=-1 

        # self.synchronizationCheckbox=QCheckBox("Sync radar/cam                ")
        # self.synchronizationCheckbox.setLayoutDirection(Qt.RightToLeft)
        self.processSaveDetectionCheckbox=QCheckBox("process/save detections")
        self.processSaveDetectionCheckbox.setLayoutDirection(Qt.RightToLeft)
        self.processSaveDetectionCheckbox.setDisabled(True)

        # self.grid.addWidget(self.synchronizationCheckbox,3,0)

        self.grid.addWidget(self.processSaveDetectionCheckbox,3,1)
        # self.parametersLayout.addLayout(self.parametersHorizontalLayout)
        
    def initTextInput(self,name,initValue,index):
        parametersHorizontalLayout=QHBoxLayout()  
        labelName = name + "Label"
        inputName = name + "Input"
        
        setattr(self,labelName,QLabel(name))
        getattr(self,labelName).setContentsMargins(20,0,0,0)
        setattr(self,inputName,QLineEdit())
       
        getattr(self,inputName).setText(str(initValue))
        getattr(self,inputName).setFixedWidth(50)
        getattr(self,inputName).setFixedWidth(50)

        # getattr(self,inputName).setAlignment(Qt.AlignLeft)

        getattr(self,inputName).setValidator(QIntValidator(bottom=0,top=2147483647))        

        parametersHorizontalLayout.addWidget(getattr(self,labelName))
        parametersHorizontalLayout.addWidget(getattr(self,inputName))
        self.grid.addLayout(parametersHorizontalLayout,index//2,index%2)
        
        

    def postProcessIndexInputOnChange(self,inputValue):
        if inputValue == "":          
            self.postProcessIndex=-1  
            self.changeWidgetsState(False)
        else:
            self.postProcessIndex=inputValue
            self.changeWidgetsState(True)

    def changeWidgetsState(self,state):

        #looping through widget bugs
        self.cameraCheckbox.setDisabled(state)        
        self.dopplerCheckbox.setDisabled(state)
        self.detectionCheckbox.setDisabled(state)

        self.noneRawRadio.setDisabled(state)
        self.noneCameraRadio.setDisabled(state)       
        self.noneDetectionRadio.setDisabled(state)
        self.noneDopplerRadio.setDisabled(state)

        self.plotDetectionRadio.setDisabled(state)
        self.plotDopplerRadio.setDisabled(state)
        self.plotRawRadio.setDisabled(state)
        self.captureCameraRadio.setDisabled(state)

        self.saveCameraRadio.setDisabled(state)
        self.saveDetectionRadio.setDisabled(state)
        self.saveDopplerRadio.setDisabled(state)
        self.saveRawRadio.setDisabled(state)
        self.cameraQualitySlider.setDisabled(state)
        # self.synchronizationCheckbox.setDisabled(state)
        for x in self.textInputs:
            if x != "postProcessIndex":
                getattr(self,x + "Input").setDisabled(state)
                getattr(self,x + "Label").setDisabled(state)
        
        self.processSaveDetectionCheckbox.setDisabled(not state)

        




        
        # self.startButton.setEnabled(True)
            

            # self.postProcessIndexInput.setEnabled(True)