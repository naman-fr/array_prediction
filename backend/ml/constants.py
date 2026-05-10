import numpy as np

# Speed of light (m/s)
C = 3e8

# Design frequencies (Hz)
FREQS = np.array([1.8e9, 1.4e9, 1.0e9])  # Sorted descending for CRT
LAMS = C / FREQS

# Synthesis of maximum unambiguous spacing
F_MIN, F_MAX = 1.0e9, 1.8e9
SYNTH_LAMBDA = C / abs(F_MAX - F_MIN)           # Synthetic wavelength
MAX_SPACING = SYNTH_LAMBDA / 2.0                 # d_m <= Lambda/2 to avoid ambiguity

# Default Signal-to-Noise Ratio (dB) for phase noise modeling
DEFAULT_SNR_DB = 20.0

