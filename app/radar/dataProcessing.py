import numpy as np

b_bandpass_coef = np.array([0.058918593549, 0.003704122993, -0.130605206968, 0, 0.130605206968, -0.003704122993, -0.058918593549])
a_bandpass_coef = np.array([1, 0.339893240317, 1.247471159638, 0.315004577848, 0.752494992039, 0.094346011045, 0.145214408359])
a_detect_coef=np.array([1.000000000000,-1.187600680176,1.305213349289,-0.674327525298,0.263469348280,-0.051753033880,0.005022526595])
b_detect_coef=np.array([0.010312874763,0.061877248576,0.154693121440,0.206257495253,0.154693121440,0.061877248576,0.010312874763])

fir4_coef = [1,-0.6 ,-0.3 ,-0.1]

class Filter:
    bp_multiscan_data=[]
    motion_multiscan_data=[]
    
    @classmethod
    def bandpass_filter(cls,x):
        N = len(x)
        y = np.zeros(N)
        
        for n in range(6, N):
            y[n] = (
                b_bandpass_coef[0] * x[n] +
                b_bandpass_coef[1] * x[n-1] +
                b_bandpass_coef[2] * x[n-2] +
                b_bandpass_coef[4] * x[n-4] +
                b_bandpass_coef[5] * x[n-5] +
                b_bandpass_coef[6] * x[n-6] -
                a_bandpass_coef[1] * y[n-1] -
                a_bandpass_coef[2] * y[n-2] -
                a_bandpass_coef[3] * y[n-3] -
                a_bandpass_coef[4] * y[n-4] -
                a_bandpass_coef[5] * y[n-5] -
                a_bandpass_coef[6] * y[n-6]
            )    
        
        cls.bp_multiscan_data.append(y) 
        if len(cls.bp_multiscan_data)> 4 : 
            cls.bp_multiscan_data.pop(0)  
        return y

    @classmethod
    def appendData(cls,newData):
        cls.bp_multiscan_data.append(newData) 
        if len(cls.bp_multiscan_data)> 4 : 
            cls.bp_multiscan_data.pop(0)  

    @classmethod
    def motionFiltered(cls):
        filteredData=[] 
        
        for i, bin in enumerate(cls.bp_multiscan_data[0]):
            # inverted coef because cls.fir_multiscan_data[3] is the most recent ...
            filteredData.append(fir4_coef[0] * cls.bp_multiscan_data[3][i] + 
                                fir4_coef[1] * cls.bp_multiscan_data[2][i] + 
                                fir4_coef[2] * cls.bp_multiscan_data[1][i] + 
                                fir4_coef[3] * cls.bp_multiscan_data[0][i])
            
        return filteredData



    @staticmethod
    def detection_lowpass_filter(x):
        N = len(x)
        y = np.zeros(N)
        for n in range(6, N):
            y[n] = (
                b_detect_coef[0] * x[n] +
                b_detect_coef[1] * x[n-1] +
                b_detect_coef[2] * x[n-2] +
                b_detect_coef[4] * x[n-4] +
                b_detect_coef[5] * x[n-5] +
                b_detect_coef[6] * x[n-6] -
                a_detect_coef[1] * y[n-1] -
                a_detect_coef[2] * y[n-2] -
                a_detect_coef[3] * y[n-3] -
                a_detect_coef[4] * y[n-4] -
                a_detect_coef[5] * y[n-5] -
                a_detect_coef[6] * y[n-6]
            )        
        return y
