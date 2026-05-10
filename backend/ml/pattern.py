import numpy as np
from backend.ml.constants import C, FREQS

def calculate_array_factor(spacings, num_points=361):
    """
    Calculate the normalized Array Factor (Radiation Pattern) for the array.
    We compute this at the highest frequency (worst case for grating lobes).
    """
    pos = np.concatenate([[0.0], np.cumsum(spacings)])
    
    # Use highest frequency
    f = FREQS[0]
    lam = C / f
    k = 2 * np.pi / lam
    
    angles_deg = np.linspace(-90, 90, num_points)
    angles_rad = np.radians(angles_deg)
    
    af_mag = []
    
    for theta in angles_rad:
        # Steering vector sum for broadside (main beam at 0 deg)
        # AF = sum(e^(j * k * p_n * sin(theta)))
        af = np.sum(np.exp(1j * k * pos * np.sin(theta)))
        # Magnitude
        af_mag.append(np.abs(af))
        
    af_mag = np.array(af_mag)
    # Normalize
    af_norm = af_mag / np.max(af_mag)
    
    # Convert to dB, clamp at -40dB for clean visualization
    af_db = 20 * np.log10(af_norm + 1e-6)
    af_db = np.clip(af_db, -40, 0)
    
    return angles_deg.tolist(), af_db.tolist()
