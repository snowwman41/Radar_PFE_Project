 
from .mainWindow import MainWindow
from common.enums import OutputType,DataMode
from config.config import Config
import time
class MainWindowController:
    def __init__(self,mainWindow : MainWindow,configSend,stopSend):
        self.configSend=configSend
        self.stopSend=stopSend
        self.mainWindow=mainWindow
        self.connectSignals()
        self.initDefaultValues()
        
    def initDefaultValues(self):
        self.mainWindow.rawCheckbox.setDisabled(True)
        self.mainWindow.detectionCheckbox.setChecked(True)
        self.mainWindow.dopplerCheckbox.setChecked(True)
        self.mainWindow.cameraCheckbox.setChecked(True)

        self.mainWindow.noneRawRadio.setChecked(True)
        self.mainWindow.noneDetectionRadio.setChecked(True)
        self.mainWindow.noneDopplerRadio.setChecked(True)
        self.mainWindow.noneCameraRadio.setChecked(True)
  
        self.mainWindow.cameraQualitySlider.setValue(5)

        self.mainWindow.detectionCheckbox.click()
        self.mainWindow.dopplerCheckbox.click()
       
        self.onCameraQualityChange(self.mainWindow.cameraQualitySlider.value())

        self.mainWindow.rawRadio=DataMode.NONE
        self.mainWindow.detectionRadio=DataMode.NONE
        self.mainWindow.dopplerRadio=DataMode.NONE
        self.mainWindow.cameraRadio=DataMode.NONE
         
    def connectSignals(self):   
        self.mainWindow.rawCheckbox.clicked.connect(self.checkboxClicked)
        self.mainWindow.detectionCheckbox.clicked.connect(self.checkboxClicked)       
        self.mainWindow.dopplerCheckbox.clicked.connect(self.checkboxClicked) 
        self.mainWindow.cameraCheckbox.clicked.connect(self.checkboxClicked)     
    
        self.mainWindow.rawRadioGroup.buttonClicked.connect(self.radioButtonGroupClicked)  
        self.mainWindow.detectionRadioGroup.buttonClicked.connect(self.radioButtonGroupClicked)  
        self.mainWindow.dopplerRadioGroup.buttonClicked.connect(self.radioButtonGroupClicked)  
        self.mainWindow.cameraRadioGroup.buttonClicked.connect(self.radioButtonGroupClicked)         

        self.mainWindow.startButton.clicked.connect(self.onClickStartButton)
        self.mainWindow.stopButton.clicked.connect(self.onClickStopButton)

        self.mainWindow.cameraQualitySlider.valueChanged.connect(self.onCameraQualityChange)

    def checkboxClicked(self):
        sender=self.mainWindow.sender()
        if (sender.objectName == OutputType.DETECTION):
            radioButtons = self.mainWindow.detectionRadioGroup.buttons()
            self.mainWindow.noneDetectionRadio.setChecked(not sender.isChecked())
            self.mainWindow.detectionRadio=DataMode.NONE if (not sender.isChecked()) else self.mainWindow.detectionRadio
            for radioButton in radioButtons:
                radioButton.setEnabled(sender.isChecked())            
            return
    
        if (self.mainWindow.sender().objectName == OutputType.DOPPLER):
            radioButtons = self.mainWindow.dopplerRadioGroup.buttons()
            self.mainWindow.noneDopplerRadio.setChecked(not sender.isChecked())
            self.mainWindow.dopplerRadio=DataMode.NONE if (not sender.isChecked()) else self.mainWindow.dopplerRadio

            for radioButton in radioButtons:
                radioButton.setEnabled(sender.isChecked())            
            return
        
        if (self.mainWindow.sender().objectName == OutputType.CAMERA):
            radioButtons = self.mainWindow.cameraRadioGroup.buttons()
            self.mainWindow.noneCameraRadio.setChecked(not sender.isChecked())
            self.mainWindow.cameraRadio=DataMode.NONE if (not sender.isChecked()) else self.mainWindow.cameraRadio

            for radioButton in radioButtons:
                radioButton.setEnabled(sender.isChecked())            
            return
            

    def onCameraQualityChange(self, value):
        self.mainWindow.cameraQualityLabel.setText(f"Saved images quality : {value}/ 10")

    def onClickStartButton(self):
        self.mainWindow.startButton.setDisabled(True)
            
        config=Config(ipAdress="192.168.1.100",
                        scanInterval=int(self.mainWindow.scanIntervalInput.text()), #us
                        userBaseII=int(self.mainWindow.BIIInput.text()),                 
                        userTxGain=63,
                        scanPerControl=65535, #infinite                        
                        R1=float(self.mainWindow.R1Input.text()),
                        R2=float(self.mainWindow.R2Input.text()),
                        NFFT=int(self.mainWindow.NFFTInput.text()),
                        timeout=200,
                        processDetection=self.mainWindow.detectionCheckbox.isChecked(),
                        processDoppler=self.mainWindow.dopplerCheckbox.isChecked(),
                        plotSaveRaw=self.mainWindow.rawRadio,
                        plotSaveDetection=self.mainWindow.detectionRadio,                  
                        plotSaveDoppler=self.mainWindow.dopplerRadio,
                        processSaveDetection=self.mainWindow.processSaveDetectionCheckbox.isChecked(),               
                        camOn=self.mainWindow.cameraCheckbox.isChecked(),
                        cameraSave=self.mainWindow.cameraRadio,
                        camSaveQuality=self.mainWindow.cameraQualitySlider.value()*10, # quality max 100
                        postProcessing=self.mainWindow.postProcessIndex
                        )        
        self.configSend.send(config)     
        
            

        
        # print(self.mainWindow.R1Input.text(),
        # self.mainWindow.R2Input.text(),
        # self.mainWindow.BIIInput.text(),
        # self.mainWindow.NFFTInput.text(),
        # self.mainWindow.detectionCheckbox.isChecked(),
        # self.mainWindow.fftCheckbox.isChecked())
        # print(self.mainWindow.rawRadio.objectName)
        
        # self.mainWindow.detectionRadio
        # self.mainWindow.fftRadio
        # self.mainWindow.cameraRadio
        # # print(self.mainWindow.rawRadioGroup.checkedButton().objectName())
        # print(self.mainWindow.cameraQualitySlider.value())
        
    def onClickStopButton(self):
        
        self.stopSend.send(1)        
        self.mainWindow.startButton.setDisabled(False)

    def radioButtonGroupClicked(self,obj):
        
        if self.mainWindow.sender() == self.mainWindow.rawRadioGroup:                    
            self.mainWindow.rawRadio=obj.objectName
        if self.mainWindow.sender() == self.mainWindow.detectionRadioGroup:
            self.mainWindow.detectionRadio=obj.objectName
        if self.mainWindow.sender() == self.mainWindow.dopplerRadioGroup:
            self.mainWindow.dopplerRadio=obj.objectName
        if self.mainWindow.sender() == self.mainWindow.cameraRadioGroup:
            self.mainWindow.cameraRadio=obj.objectName