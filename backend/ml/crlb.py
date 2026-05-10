import numpy as np
from ml.constants import C

def calculate_crlb_rms(spacings, freqs, angles, snr_db):
    """
    Calculate the theoretical Cramer-Rao Lower Bound (CRLB) RMS error 
    for a given non-uniform linear array over a set of angles and frequencies.
    """
    snr_linear = 10 ** (snr_db / 10.0)
    
    # Antenna positions
    pos = np.concatenate([[0.0], np.cumsum(spacings)])
    N = len(pos)
    
    # Position variance
    pos_center = np.mean(pos)
    pos_var = np.mean((pos - pos_center)**2)
    
    crlb_variances = []
    
    for theta in angles:
        cos_theta = np.cos(np.radians(theta))
        # Avoid division by zero at endfire
        if abs(cos_theta) < 1e-6:
            cos_theta = 1e-6
            
        for f in freqs:
            lam = C / f
            # CRLB for a single frequency and angle
            # Formula: lambda^2 / (8 * pi^2 * SNR * N * pos_var * cos^2(theta))
            var_theta = (lam**2) / (8 * (np.pi**2) * snr_linear * N * pos_var * (cos_theta**2))
            crlb_variances.append(var_theta)
            
    # The average variance across frequencies and angles gives us a single metric
    avg_variance = np.mean(crlb_variances)
    
    # Convert variance (radians^2) to std deviation (degrees)
    crlb_rms_deg = np.degrees(np.sqrt(avg_variance))
    
    return crlb_rms_deg
