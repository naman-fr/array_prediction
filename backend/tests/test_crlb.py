import numpy as np
from ml.crlb import calculate_crlb_rms
from ml.constants import FREQS

def test_calculate_crlb_rms():
    spacings = [0.1, 0.1, 0.1]
    angles = np.array([-10, 0, 10])
    
    # Calculate for a high SNR
    crlb_high_snr = calculate_crlb_rms(spacings, FREQS, angles, snr_db=30)
    
    # Calculate for a low SNR
    crlb_low_snr = calculate_crlb_rms(spacings, FREQS, angles, snr_db=10)
    
    assert isinstance(crlb_high_snr, float)
    assert isinstance(crlb_low_snr, float)
    
    # CRLB should be higher (worse) when SNR is lower
    assert crlb_low_snr > crlb_high_snr
