
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt

# Define the filter coefficients
b =np.array([1,-1])
a =1

# Compute the frequency response
w, h = signal.freqz(b, a)

# Plot the magnitude response
plt.figure()
plt.plot(w, np.abs(h), 'b')
plt.title('Magnitude Response')
plt.ylabel('Amplitude')
plt.xlabel('Frequency [rad/sample]')
plt.grid()

# Find the cutoff frequency (-3dB point)
cutoff_freq = w[np.argmin(np.abs(np.abs(h) - 0.707 * np.max(np.abs(h))))]

# Add cutoff frequency line to the plot
plt.axvline(x=cutoff_freq, color='r', linestyle='--', label=f'Cutoff Frequency: {cutoff_freq:.2f} rad/sample')
plt.legend()

# Plot the phase response
plt.figure()
plt.plot(w, np.unwrap(np.angle(h)), 'g')
plt.title('Phase Response')
plt.ylabel('Phase (radians)')
plt.xlabel('Frequency [rad/sample]')
plt.grid()

plt.show()
