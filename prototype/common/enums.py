from enum import Enum

class FileType(Enum):
    SCAN=0
    DETECTION= 1
    FFT= 2
    CAMERA=4
    NODETECTION= 5

class OutputType(Enum):
    RAW=0
    DETECTION= 1
    DOPPLER= 2
    CAMERA=3

class DataMode(Enum):
    NONE=0
    PLOT=1
    SAVE=2